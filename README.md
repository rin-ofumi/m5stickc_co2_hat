# co2_hat
MicroPython project / Co2 HAT & M5StickC / Data storage uses Ambient

<br>

# <概要>

![Ambient_Co2_0](https://kitto-yakudatsu.com/wp/wp-content/uploads/2019/11/DSC_0894-scaled.jpg)

<br>

* M5StickCとNDIR式（光学式）CO2センサー「MH-Z19B」を使って、環境のCO2濃度を測定するプログラムです。
* 「MH-Z19B」をM5StickCへ簡単に装着する為の「Co2 HATキット」（[BOOTHで販売中](https://kitto-yakudatsu.booth.pm/items/1671574)）を使えば、綺麗にケースに収まった状態で使用できます。
* AmbientというIoTデータ可視化サービスを使って、記録を残すことも可能です。（無料枠で使えます）
* MicroPythonで記述しています。（ファームウェアは UIFlow 1.6.2 を使用）

<br>
<br>

この様なCO2濃度グラフを取得出来るようになります。

![Ambient_Co2_1](https://kitto-yakudatsu.com/wp/wp-content/uploads/2019/11/co2_hat_graph.png)

<br>

# <実行に必要なファイル>

## Ambientライブラリ「ambient.py」※オプション
Ambientへのデータ送信（記録）を使う場合は、[こちら](https://github.com/AmbientDataInc/ambient-python-lib)のライブラリが必要です。<br>
「ambient.py」を親機のM5StickCのルートに保存して下さい。<br>

<br>

## プログラム本体「test_CO2_Ambient.py」**※必須**
M5StickC・M5StickCPlus用です。（プログラム内で機種自動判別させてます）<br>
M5StickCのプログラム選択モード「APP.List」から起動させる場合は、親機のM5StickCの「Apps」配下に保存して下さい。<br>

<br>

## 設定ファイル「co2_set.txt」**※オプション**

* AmbientでCO2濃度を記録する場合は、「チャネルID」を「AM_ID:」以降に、「ライトキー」を「AM_WKEY:」以降に追記して下さい。
* CO2濃度の警告閾値を「CO2_RED:」以降に追記して下さい。（単位はppm）

※全てにおいて、空白文字、"などは含まない様にして下さい<br>
修正後、親機のM5StickCのルートに保存して下さい。<br>

<br>

# <使い方>

## 基本動作

- プログラムを起動させると、M5StickCの画面に時刻が現れ、更に数秒でCO2測定値が表示されます。
- 5秒毎にCO2測定値を「MH-Z19B」から得て画面を更新しています。
- 1分毎にCO2測定値をAmbientへ送信しています。（オプション設定した場合）
- 時刻が赤文字の時はAmbientへの通信が出来ていない事を示します。（**初回通信してない起動直後は時計は赤文字**）
- 「MH-Z19B」からの応答が[TIMEOUT]秒以上無かった場合にCO2測定値表示が消えます。（異常時判断）

<br>

## M5StickC/Plus版のボタン操作

- Aボタン（M5ロゴの有るボタン）を押すと画面消灯します。もう一度押すと画面点灯します。（CO2濃度が警告閾値を超えてる場合は、強制点灯されます）
- Bボタン（電源ボタンじゃない方の側面ボタン）を押すと表示が180度回転しますので、設置向きに合わせてお選び下さい。

![M5StickC_1](https://kitto-yakudatsu.com/wp/wp-content/uploads/2019/11/P1230597-scaled.jpg)

![M5StickC_2](https://kitto-yakudatsu.com/wp/wp-content/uploads/2019/11/P1230596-scaled.jpg)

![M5StickC_3](https://kitto-yakudatsu.com/wp/wp-content/uploads/2019/11/P1230600-scaled.jpg)

![M5StickC_4](https://kitto-yakudatsu.com/wp/wp-content/uploads/2019/11/P1230601-scaled.jpg)

<br>

# <参考ページ>
その他の情報については[ブログ](https://kitto-yakudatsu.com/archives/7286)をご参照下さい。<br>

<br>

# <アップデート履歴>

## 【2020.09.05】 [test_CO2_Ambient.py] Update!

* M5StickCPlus対応（M5StickC版と同じソースコードで動作します）
* その他バグFix。
* ファイル毎の改行コード混在の是正。（LFに統一しました）

<br>

## 【2020.09.02】 [test_CO2_Ambient.py] Update!

* UIFlow-v1.6.2 ファームへの対応。（公式同梱になったntptimeモジュールに合わせた修正）

<br>

## 【2020.04.22】 [CO2_zeropoint.py] Update!

* @takashyxさんからのプルリクエストをマージ（ZERO POINT CALIBRATIONコマンド送信タイミングの間違いを修正）

<br>

## 【2019.12.14】 [test_CO2_Ambient.py] Update!

* UIFlow-v1.4.2 ファームへの対応。
* AmbientのチャネルID桁数チェックの削除。（5桁縛りだと勘違いしてました）

<br>

## 【2019.12.14】 [CO2_zeropoint.py] Update!

* UIFlow-v1.4.2 ファームへの対応。

<br>

## 【2019.11.13】[CO2_zeropoint.py] add

* ゼロポイントキャリブレーション用サンプルプログラム追加（説明は省きます。MH-Z19Bの仕様書を読んで、環境構築も含め、ソースが分かる方だけお使い下さい。）

<br>

## 【2019.11.13】

* 最初のリリース

