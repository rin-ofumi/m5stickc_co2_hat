from m5stack import *
import machine
import gc
import utime
import uos
import _thread


# 定数宣言
AM_INTERVAL         = 60    # Ambientへデータを送るサイクル（秒）
CO2_INTERVAL        = 5     # MH-19Bへco2測定値要求コマンドを送るサイクル（秒）
TIMEOUT             = 30    # 何らかの事情でCO2更新が止まった時のタイムアウト（秒）のデフォルト値
CO2_RED             = 1000  # co2濃度の換気警告閾値（ppm）のデフォルト値
CO2_MAX             = 2000  # co2測定値のグラフ表示上限値
CO2_MIN             = 400   # co2測定値のグラフ表示下限値
CO2_TREND_MARGIN    = 10    # co2トレンド比較時に"stay"として扱う差分
AM_ID               = None  # AmbientのチャネルID
AM_WKEY             = None  # Ambientのライトキー

# 変数宣言
Am_st               = 0     # Ambient設定   [0:無し(WiFiも未使用になる)、1:設定有＆初回通信待ち、2:設定有＆通信OK、3:設定有＆通信NG]
Disp_angle          = 0     # 画面方向      [0:電源ボタンが上、1:電源ボタンが下]
Disp_mode           = 0     # 表示モード    [0:数値表示、1:トレンドグラフ表示、2:トレンドグラフ表示（値表示有）]
data_mute           = False # co2応答が一定時間無い場合の表示オフ用     [True:表示オフ(黒文字化)]
m5type              = 0     # 無印かPlusか  [0:M5StickC、1:M5StickCPlus]
co2                 = 0     # co2測定値（最新）
co2_log             = [0] * 240 # co2値履歴（5秒毎測定の場合、240回分はおおよそ20分）


# @cinimlさんのファーム差分吸収ロジック
class AXPCompat(object):
    def __init__(self):
        if( hasattr(axp, 'setLDO2Vol') ):
            self.setLDO2Vol = axp.setLDO2Vol
        else:
            self.setLDO2Vol = axp.setLDO2Volt

axp = AXPCompat()


# 表示モード切替ボタン処理スレッド関数
def buttonA_wasPressed():
    global Disp_mode

    if Disp_mode >= 2 :
        Disp_mode = 0
    else :
        Disp_mode = Disp_mode + 1

    draw_lcd()


# 画面向き切替ボタン処理スレッド関数
def buttonB_wasPressed():
    global Disp_angle

    if Disp_angle == 1 :
        Disp_angle = 0
    else :
        Disp_angle = 1
    
    draw_lcd()


# 表示変更時の処理振り分け
def draw_lcd():
    lcd.clear()

    if Disp_mode == 0 :
        draw_value()
    if Disp_mode >= 1 :
        draw_graph()

    draw_status()


# Ambient通信ステータスマーカー表示処理関数
def draw_status():
                        # Ambientステータス [0:設定無し、1:設定有＆初回通信待ち、2:設定有＆通信OK、3:設定有＆通信NG]
    if Am_st == 1 :     # Ambient設定有＆初回通信待ち ⇒ 白枠、中黒
        c_o = lcd.WHITE
        c_f = lcd.BLACK
    elif Am_st == 2 :   # Ambient設定有＆通信OK ⇒ 白枠、中緑
        c_o = lcd.WHITE
        c_f = lcd.GREEN
    elif Am_st == 3 :   # Ambient設定有＆通信NG ⇒ 白枠、中赤
        c_o = lcd.WHITE
        c_f = lcd.RED

    c_offset = 3    # Ambient通信ステータスマーカーの画面端からのオフセット量

    # M5StickC(無印)向け
    if m5type == 0 :
        c_r = 7
        if Disp_angle == 0 :    # [0:電源ボタンが上、1:電源ボタンが下]
            c_x = 0 + c_r + c_offset
            c_y = 159 - c_r - c_offset
        if Disp_angle == 1 :
            c_x = 79 - c_r - c_offset
            c_y = 0 + c_r + c_offset
    # M5StickCPlus向け
    if m5type == 1 :
        c_r = 10
        if Disp_angle == 0 :    # [0:電源ボタンが上、1:電源ボタンが下]
            c_x = 0 + c_r + c_offset
            c_y = 239 - c_r - c_offset
        if Disp_angle == 1 :
            c_x = 134 - c_r - c_offset
            c_y = 0 + c_r + c_offset

    if Am_st > 0 :  # Ambient設定有ならAmbient通信ステータスマーカー描画
        lcd.circle(c_x, c_y, c_r, c_o, c_f)


# 濃度グラフ表示モード処理関数 (Disp_mode = 1 or 2)
def draw_graph():
    if Disp_mode == 1 :
        l_c = lcd.WHITE
    if Disp_mode == 2 :
        l_c = lcd.DARKGREY

    if co2 >= CO2_RED :  # CO2濃度閾値超え時は文字が赤くなる
        fc = lcd.RED
    else :
        fc = lcd.WHITE
    
    # M5StickC(無印)向け
    if m5type == 0 :
        # CO2グラフ表示
        if Disp_angle == 0 : # [0:電源ボタンが上]
            lcd.rect(0 , 0, 79 - int((CO2_RED - CO2_MIN) * (80 / (CO2_MAX - CO2_MIN))), 160, 0x440000, 0x440000) # 換気警告ゾーン
            for n in range(159) :
                x_start = 79 - int((co2_log[n] - CO2_MIN) * (80 / (CO2_MAX - CO2_MIN)))
                x_end   = 79 - int((co2_log[n + 1] - CO2_MIN) * (80 / (CO2_MAX - CO2_MIN)))
                lcd.line(x_start, n, x_end, n + 1, l_c)
        if Disp_angle == 1 : # [1:電源ボタンが下]
            lcd.rect(int((CO2_RED - CO2_MIN) * (80 / (CO2_MAX - CO2_MIN))), 0, 79 , 160, 0x440000, 0x440000) # 換気警告ゾーン
            for n in range(159) :
                x_start = int((co2_log[n] - CO2_MIN) * (80 / (CO2_MAX - CO2_MIN)))
                x_end   = int((co2_log[n + 1] - CO2_MIN) * (80 / (CO2_MAX - CO2_MIN)))
                lcd.line(x_start, 159 - n, x_end, 159 - (n + 1), l_c)

        # Disp_mode=2ならCO2値表示
        if Disp_mode == 2 :
            if Disp_angle == 0 : # [0:電源ボタンが上]
                lcd.font(lcd.FONT_DejaVu18, rotate = 270) # 単位(ppm)の表示
                lcd.print('ppm', 55, 60, fc)
                if data_mute != True :
                    lcd.font(lcd.FONT_DejaVu40, rotate = 270) # co2値の表示
                    lcd.print(str(co2), 21, 24 + (len(str(co2))* 24), fc)
            if Disp_angle == 1 : # [1:電源ボタンが下]
                lcd.font(lcd.FONT_DejaVu18, rotate = 90) # 単位(ppm)の表示
                lcd.print('ppm', 24, 100, fc)
                if data_mute != True :
                    lcd.font(lcd.FONT_DejaVu40, rotate = 90) # co2値の表示
                    lcd.print(str(co2), 56, 133 - (len(str(co2))* 24), fc)

    # M5StickCPlus向け
    if m5type == 1 :
        # CO2グラフ表示
        if Disp_angle == 0 : # [0:電源ボタンが上]
            lcd.rect(0 , 0, 134 - int((CO2_RED - CO2_MIN) * (135 / (CO2_MAX - CO2_MIN))), 240, 0x440000, 0x440000) # 換気警告ゾーン
            for n in range(239) :
                x_start = 134 - int((co2_log[n] - CO2_MIN) * (135 / (CO2_MAX - CO2_MIN)))
                x_end   = 134 - int((co2_log[n + 1] - CO2_MIN) * (135 / (CO2_MAX - CO2_MIN)))
                lcd.line(x_start, n, x_end, n + 1, l_c)
        if Disp_angle == 1 : # [1:電源ボタンが下]
            lcd.rect(int((CO2_RED - CO2_MIN) * (135 / (CO2_MAX - CO2_MIN))), 0, 134 , 240, 0x440000, 0x440000) # 換気警告ゾーン
            for n in range(239) :
                x_start = int((co2_log[n] - CO2_MIN) * (135 / (CO2_MAX - CO2_MIN)))
                x_end   = int((co2_log[n + 1] - CO2_MIN) * (135 / (CO2_MAX - CO2_MIN)))
                lcd.line(x_start, 239 - n, x_end, 239 - (n + 1), l_c)

        # Disp_mode=2ならCO2値表示
        if Disp_mode == 2 :
            # CO2文字列の表示揃え用の位置オフセット
            if len(str(co2)) > 3 :
                str_offset = 0
            else :
                str_offset = 32
            
            if Disp_angle == 0 : # [0:電源ボタンが上]
                lcd.font(lcd.FONT_DejaVu24, rotate = 270) # 単位(ppm)の表示
                lcd.print('ppm', 93, 97, fc)
                if data_mute != True :
                    lcd.font(lcd.FONT_DejaVu56, rotate = 270) # co2値の表示
                    lcd.print(str(co2), 45, 185 - str_offset, fc)
            if Disp_angle == 1 : # [1:電源ボタンが下]
                lcd.font(lcd.FONT_DejaVu24, rotate = 90) # 単位(ppm)の表示
                lcd.print('ppm', 44, 146, fc)
                if data_mute != True :
                    lcd.font(lcd.FONT_DejaVu56, rotate = 90) # co2値の表示
                    lcd.print(str(co2), 92, 55 + str_offset, fc)


# 測定値表示モードの処理関数 (Disp_mode = 0)
def draw_value():
    # 表示ミュートされてるか、初期値のままならco2値非表示（黒文字化）
    if (data_mute == True) or (co2 == 0) :
        fc = lcd.BLACK
    else :
        if co2 >= CO2_RED :  # CO2濃度閾値超え時は文字が赤くなる
            fc = lcd.RED
        else :
            fc = lcd.WHITE

    # トレンド計算 [0:データ蓄積待ち（初期値）、1:up、2:stay、3:down]
    if co2_log[59] == 0 :   # 60個目のデータが初期値じゃなくなるまで（5分経つまで）はトレンド処理無し
        co2_trend = 0
    else :
        co2_log_5min = 0
        for n in range(60) :  # 直近5分の平均値　※5秒毎サンプルの場合
            co2_log_5min = co2_log_5min + co2_log[n]
        co2_log_5min = co2_log_5min / 60

        co2_log_30sec = 0
        for n in range(6) :   # 直近30秒の平均値　※5秒毎サンプルの場合
            co2_log_30sec = co2_log_30sec + co2_log[n]
        co2_log_30sec = co2_log_30sec / 6
        print('5min = ' + str(co2_log_5min) + ' / 30sec = ' + str(co2_log_30sec))

        if ( co2_log_30sec - co2_log_5min ) >= CO2_TREND_MARGIN :
            co2_trend = 1
        elif ( co2_log_5min - co2_log_30sec ) >= CO2_TREND_MARGIN :
            co2_trend = 3
        else :
            co2_trend = 2

    # M5StickC(無印)向け
    if m5type == 0 :
        # CO2値表示
        if Disp_angle == 0 : # [0:電源ボタンが上]
            lcd.font(lcd.FONT_DejaVu18, rotate = 270) # 単位(ppm)の表示
            lcd.print('ppm', 55, 60, fc)
            lcd.font(lcd.FONT_DejaVu40, rotate = 270) # co2値の表示
            lcd.print(str(co2), 21, 24 + (len(str(co2))* 24), fc)
        if Disp_angle == 1 : # [1:電源ボタンが下]
            lcd.font(lcd.FONT_DejaVu18, rotate = 90) # 単位(ppm)の表示
            lcd.print('ppm', 24, 100, fc)
            lcd.font(lcd.FONT_DejaVu40, rotate = 90) # co2値の表示
            lcd.print(str(co2), 56, 133 - (len(str(co2))* 24), fc)

    # M5StickCPlus向け
    if m5type == 1 :
        # CO2文字列の表示揃え用の位置オフセット
        if len(str(co2)) > 3 :
            str_offset = 0
        else :
            str_offset = 32
        # CO2値表示
        if Disp_angle == 0 : # [0:電源ボタンが上]
            lcd.font(lcd.FONT_DejaVu24, rotate = 270) # 単位(ppm)の表示
            lcd.print('ppm', 93, 77, fc)
            lcd.font(lcd.FONT_DejaVu56, rotate = 270) # co2値の表示
            lcd.print(str(co2), 45, 155 - str_offset, fc)
        if Disp_angle == 1 : # [1:電源ボタンが下]
            lcd.font(lcd.FONT_DejaVu24, rotate = 90) # 単位(ppm)の表示
            lcd.print('ppm', 44, 166, fc)
            lcd.font(lcd.FONT_DejaVu56, rotate = 90) # co2値の表示
            lcd.print(str(co2), 92, 85 + str_offset, fc)

        # トレンドマーカー表示（M5StickCPlusのみ）
        if Disp_angle == 0 : # [0:電源ボタンが上]
            m_x = 67
            m_y = 200
            if co2_trend == 1 :
                lcd.triangle(m_x, m_y - 15, m_x - 15, m_y, m_x, m_y + 15, lcd.WHITE, lcd.WHITE)
                lcd.rect(m_x, m_y - 5, 25, 10, lcd.WHITE, lcd.WHITE)
            elif co2_trend == 2 :
                lcd.triangle(m_x - 15, m_y, m_x, m_y - 15, m_x + 15, m_y, lcd.WHITE, lcd.WHITE)
                lcd.rect(m_x - 5 , m_y, 10, 15, lcd.WHITE, lcd.WHITE)
            elif co2_trend == 3 :
                lcd.triangle(m_x, m_y - 15, m_x + 15, m_y, m_x, m_y + 15, lcd.WHITE, lcd.WHITE)
                lcd.rect(m_x - 25, m_y - 5, 25, 10, lcd.WHITE, lcd.WHITE)
        if Disp_angle == 1 : # [1:電源ボタンが下]
            m_x = 67
            m_y = 40
            if co2_trend == 1 :
                lcd.triangle(m_x, m_y - 15, m_x + 15, m_y, m_x, m_y + 15, lcd.WHITE, lcd.WHITE)
                lcd.rect(m_x - 25, m_y - 5, 25, 10, lcd.WHITE, lcd.WHITE)
            elif co2_trend == 2 :
                lcd.triangle(m_x - 15, m_y, m_x, m_y + 15, m_x + 15, m_y, lcd.WHITE, lcd.WHITE)
                lcd.rect(m_x - 5 , m_y - 15, 10, 15, lcd.WHITE, lcd.WHITE)
            elif co2_trend == 3 :
                lcd.triangle(m_x, m_y - 15, m_x - 15, m_y, m_x, m_y + 15, lcd.WHITE, lcd.WHITE)
                lcd.rect(m_x, m_y - 5, 25, 10, lcd.WHITE, lcd.WHITE)


# MH-Z19Bデータのチェックサム確認関数
def checksum_chk(data):
    sum = 0
    for a in data[1:8]:
        sum = (sum + a) & 0xff
    c_sum = 0xff - sum + 1
    if c_sum == data[8]:
        return True
    else:
        print("c_sum un match!!")
        return False


# co2_set.txtの存在/中身チェック関数
def co2_set_filechk():
    global CO2_RED
    global TIMEOUT
    global AM_ID
    global AM_WKEY

    scanfile_flg = False
    for file_name in uos.listdir('/flash') :
        if file_name == 'co2_set.txt' :
            scanfile_flg = True
    
    if scanfile_flg :
        print('>> found [co2_set.txt] !')
        with open('/flash/co2_set.txt' , 'r') as f :
            for file_line in f :
                filetxt = file_line.strip().split(':')
                if filetxt[0] == 'CO2_RED' :
                    if int(filetxt[1]) >= 1 :
                        CO2_RED = int(filetxt[1])
                        print('- CO2_RED: ' + str(CO2_RED))
                elif filetxt[0] == 'TIMEOUT' :
                    if int(filetxt[1]) >= 1 :
                        TIMEOUT = int(filetxt[1])
                        print('- TIMEOUT: ' + str(TIMEOUT))
                elif filetxt[0] == 'AM_ID' :
                    AM_ID = str(filetxt[1])
                    print('- AM_ID: ' + str(AM_ID))
                elif filetxt[0] == 'AM_WKEY' :
                    if len(filetxt[1]) == 16 :
                        AM_WKEY = str(filetxt[1])
                        print('- AM_WKEY: ' + str(AM_WKEY))
    else :
        print('>> no [co2_set.txt] !')       
    return scanfile_flg


# メインプログラムはここから（この上はプログラム内関数）


# 画面初期化
axp.setLDO2Vol(2.7) #バックライト輝度調整（中くらい）

if lcd.winsize() == (80,160) :  # M5StickC/Plus機種判定
    m5type = 0
    print('>> M5Type = M5StickC')
if lcd.winsize() == (136,241) :
    m5type = 1
    print('>> M5Type = M5StickCPlus')

draw_lcd()


# MH-19B/C UART,GPIO設定
#mhz19b = machine.UART(1, tx=0, rx=26)   # for Rev0.1
mhz19b = machine.UART(1, tx=0, rx=36)  # for Rev0.2
mhz19b.init(9600, bits=8, parity=None, stop=1)

# 電源ONでMH-Z19のキャリブレーション処理が起こらない様に、HD端子(G26)を出力＆Highにしておく for Rev0.2
# ※下記のG26の設定は、M5StickC後期版かPlusの方のみ使えます。HD端子はジャンパーでG26に繋いで下さい。
# ※M5StickC初期版(電源OFFで[5V OUT]がオフにならないるタイプ)の方は、HD端子を未接続にして下記2行をコメントアウトして下さい。
#pinout = machine.Pin(26, machine.Pin.OUT)
#pinout.value(1)


# UARTの送受信バッファーの塵データをクリア
utime.sleep(0.5)
if mhz19b.any() != 0 :
    dust = mhz19b.read()
mhz19b.write('\r\n')
utime.sleep(0.5)
print('>> UART RX/TX Data Clear!')


# ユーザー設定ファイル読み込み
co2_set_filechk()


# Ambient設定（Ambient設定がある場合のみWiFi接続）
if (AM_ID is not None) and (AM_WKEY is not None) : # Ambient設定情報があった場合
    # WiFi設定
    import wifiCfg
    wifiCfg.autoConnect(lcdShow=True)
    import ambient
    am_co2 = ambient.Ambient(AM_ID, AM_WKEY)
    Am_st = 1
else : # Ambient設定情報が無かった場合
    Am_st = 0


# ボタン検出スレッド起動
btnA.wasPressed(buttonA_wasPressed)
btnB.wasPressed(buttonB_wasPressed)


# タイムカウンタ初期値設定
co2_tc = utime.time()
am_tc = utime.time()


# メインルーチン
while True:
    if (utime.time() - co2_tc) >= CO2_INTERVAL : # co2要求コマンド送信
        d_rdy = False
        while d_rdy == False :
            mhz19b_data = bytearray(9)
            mhz19b.write(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79')   # co2測定値リクエスト
            print('>> CO2 data request')
            utime.sleep(0.1)
            if mhz19b.any() == 9 :  # 受信データ処理（9バイトが正常なデータ）
                mhz19b.readinto(mhz19b_data, len(mhz19b_data))
                d_rdy = True
                # co2測定値リクエストの応答
                if mhz19b_data[0] == 0xff and mhz19b_data[1] == 0x86 and checksum_chk(mhz19b_data) == True :    # 応答かどうかの判定とチェックサムチェック
                    co2_tc = utime.time()
                    co2 = mhz19b_data[2] * 256 + mhz19b_data[3]
                    co2_log.insert(0, co2)   # co2_logの先頭[0]に測定値を追加
                    del co2_log[-1]          # co2_logの末尾を削除
                    data_mute = False
                    print(str(co2) + ' ppm / ' + str(co2_tc))
                    if Am_st >= 1 :  # Ambient設定情報があった場合
                        if (utime.time() - am_tc) >= AM_INTERVAL :      # インターバル値の間隔でAmbientへsendする
                            am_tc = utime.time()
                            try :                                       # ネットワーク不通発生などで例外エラー終了されない様に try except しとく
                                r = am_co2.send({'d1': co2})
                                print('Ambient send OK! / ' + str(r.status_code) + ' / ' + str(Am_st))
                                Am_st = 2
                                am_tc = utime.time()
                                r.close()
                            except:
                                print('Ambient send ERR! / ' + str(Am_st))
                                Am_st = 3
                    draw_lcd()
            else :  # 9バイト以外のデータを受信した場合は破棄
                print('Received an abnormal value!! :' + str(mhz19b.any()))
                dust = mhz19b.read()
                utime.sleep(1)
    
    if (utime.time() - co2_tc) >= TIMEOUT : # co2応答が一定時間無い場合はCO2値表示オフ
        data_mute = True
        co2 = 0
        draw_lcd()
	
    utime.sleep(0.1)
    gc.collect()    
