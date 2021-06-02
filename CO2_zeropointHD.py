# MH-Z19B/Cの「Zero Point Calibration Hand-operated method」を実行するプログラムです。
# CO2センサーのメーカーの仕様書を読み、内容が理解できる方のみ実施して下さい。
# Co2 HAT（rev0.2以上）が必要となります。ジャンパーピン設定、GPIO割当を正しく実施して実行して下さい。

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


# MH-19B/C GPIO設定  念のためMH-Z19のHD端子(G26)をHighにしておく for Rev0.2
pinout = machine.Pin(26, machine.Pin.OUT)   
pinout.value(1)


# タイムカウンタ初期値設定
zero_tc = utime.time()


lcd.print('Zero Calibration Start!', 0, 20)
utime.sleep(2)


# 20分待つ（余裕見て21分）
while utime.time() < zero_tc + (21*60) :
    lcd.clear()
    lcd.print(str(zero_tc + (21*60) - utime.time()), 20, 20)
    utime.sleep(1)


# ZERO POINT CALIBRATION HD端子制御 for Rev0.2
pinout = machine.Pin(26, machine.Pin.OUT)
pinout.value(0) # HD端子(G26)をLowにする（Lowレベルを7秒以上維持でゼロポイントキャリブレーション）
lcd.clear()
lcd.print('HD port is Low!', 0, 20)
utime.sleep(8) # 仕様書上は7秒だけど、念のため1秒多くしとく
pinout.value(1) # 時間を満たしたらHDをHighに戻す
lcd.clear()
lcd.print('HD port is High!', 0, 20)
utime.sleep(2)


lcd.clear()
lcd.print('Zero Calibration End', 0, 20)