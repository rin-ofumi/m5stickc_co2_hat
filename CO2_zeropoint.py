from m5stack import *
import machine
import utime


# @cinimlさんのファーム差分吸収ロジック
class AXPCompat(object):
    def __init__(self):
        if( hasattr(axp, 'setLDO2Vol') ):
            self.setLDO2Vol = axp.setLDO2Vol
        else:
            self.setLDO2Vol = axp.setLDO2Volt

axp = AXPCompat()


# 画面初期化
axp.setLDO2Vol(2.7) #バックライト輝度調整（中くらい）
lcd.clear()


# MH-19B/C UART,GPIO設定    for Rev0.1
#mhz19b = machine.UART(1, tx=0, rx=26)
#mhz19b.init(9600, bits=8, parity=None, stop=1)

# MH-19B/C UART,GPIO設定    for Rev0.2
mhz19b = machine.UART(1, tx=0, rx=36)
mhz19b.init(9600, bits=8, parity=None, stop=1)


# 電源ONでMH-Z19のキャリブレーション処理が起こらない様に、HD端子(G26)を出力＆Highにしておく for Rev0.2
# ※下記のG26の設定は、M5StickC後期版かPlusの方のみ使えます。HD端子はジャンパーでG26に繋いで下さい。
# ※M5StickC初期版(電源OFFで[5V OUT]がオフにならないるタイプ)の方は、HD端子を未接続にして下記2行をコメントアウトして下さい。
#pinout = machine.Pin(26, machine.Pin.OUT)
#pinout.value(1)


# タイムカウンタ初期値設定
zero_tc = utime.time()


lcd.print('Zero Calibration Start!', 0, 20)
utime.sleep(2)


# 20分待つ（余裕見て21分）
while utime.time() < zero_tc + (21*60) :
    lcd.clear()
    lcd.print(str(zero_tc + (21*60) - utime.time()), 20, 20)
    utime.sleep(1)

# ZERO POINT CALIBRATION コマンド送信
mhz19b.write(b'\xff\x01\x87\x00\x00\x00\x00\x00\x78')
utime.sleep(2)

lcd.clear()
lcd.print('Zero Calibration End', 0, 20)