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


# MH-19B UART設定
mhz19b = machine.UART(1, tx=0, rx=26)
mhz19b.init(9600, bits=8, parity=None, stop=1)


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