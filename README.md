# co2_hat
MicroPython project / Co2 HAT & M5StickC / Data storage uses Ambient

<br>

# <概要>

![Co2_socket_0](https://kitto-yakudatsu.com/wp/wp-content/uploads/2021/02/P1300152-scaled.jpg)

<br>

* M5StickCとNDIR式（光学式）CO2センサー「MH-Z19B」や「MH-Z19C」を使って、環境のCO2濃度を測定するプログラムです。
* 「MH-Z19B」をM5StickCへ簡単に装着する為の[「Co2 HATキット」](https://kitto-yakudatsu.booth.pm/items/1671574)を使えば、綺麗にケースに収まった状態で使用できます。
* 他に、[秋月電子で販売されているピンヘッダー付きの「MH-Z19C」](https://akizukidenshi.com/catalog/g/gM-16142/)に対応した[「Co2 HAT（ソケット版）キット」](https://kitto-yakudatsu.booth.pm/items/2780399)もあります。（コチラは半田付け不要で、より簡単に使用出来ます。）
* AmbientというIoTデータ可視化サービスを使って、記録を残すことも可能です。（無料枠で使えます）
* MicroPythonで記述しています。（ファームウェアは UIFlow 1.8.5 を使用）

<br>
<br>

この様なCO2濃度グラフを取得出来るようになります。

![Ambient_Co2_1](https://kitto-yakudatsu.com/wp/wp-content/uploads/2019/11/co2_hat_graph.png)

<br>

# <実行に必要なファイル>

## Ambientライブラリ「ambient.py」※オプション
Ambientへのデータ送信（記録）を使う場合は、[こちら](https://github.com/AmbientDataInc/ambient-python-lib)のライブラリが必要です。<br>
「ambient.py」をM5StickCのルートに保存して下さい。<br>

<br>

## プログラム本体「test_CO2_Ambient.py」**※必須**
M5StickC・M5StickCPlus用です。（プログラム内で機種自動判別させてます）<br>
M5StickCのプログラム選択モード「APP.List」から起動させる場合は、M5StickCの「Apps」配下に保存して下さい。<br>

※2021/5/31以降の販売分より、シリアルポート割当てピンが変更されています。（Rev 0.1: tx=0,rx=26 ⇒ Rev 0.2: tx=0,rx=36）<br>
※尚、公開しているプログラムは Rev 0.2 をデフォルトとしております。<br>
※旧Revをお使いの場合は235～241行目のコメントアウト部位を入れ換えて使用して下さい。（詳しくはコード内コメントを参照願います）<br>

<br>

## 設定ファイル「co2_set.txt」**※オプション**

* AmbientでCO2濃度を記録する場合は、「チャネルID」を「AM_ID:」以降に、「ライトキー」を「AM_WKEY:」以降に追記して下さい。
* ※上記設定を行わなかった場合は、Ambientへの送信も行われませんし、WiFi通信も行われません。
* CO2濃度の警告閾値を「CO2_RED:」以降に追記して下さい。（単位はppmで、初期値は厚労省推奨換気目安の1000としてます。）

※全てにおいて、空白文字、"などは含まない様にして下さい<br>
※修正後、M5StickCのルートに保存して下さい。<br>

<br>

# <使い方>

## 基本動作

- プログラムを起動させると、M5StickCの画面が黒画になり、更に5秒ほど経つとCO2測定値が表示されます。
- 5秒毎にCO2測定値を「MH-Z19B/C」から得て画面を更新しています。
- 1分毎にCO2測定値をAmbientへ送信しています。（オプション設定した場合）
- 「co2_set.txt」にてAmbient設定を行っている場合は、M5StickCの画面左上に丸マーカーが表示されます。
- 「co2_set.txt」にてAmbient設定を行っていない場合は、丸マーカーは表示されず、WiFi通信も行いません。（WiFi環境が無い所でお使いの場合はこの設定をご利用ください。）
- 丸マーカーが白枠のみの場合は、Ambientの初回送信待ちです。Ambientへの送信が成功すると、緑のマーカーになります。
- なんらかの事情でAmbientへの送信が出来なかった場合は、赤のマーカーになります。
- 「MH-Z19B/C」からの応答が[TIMEOUT]秒以上無かった場合にCO2測定値表示が消えます。（異常時判断）
- 画面表示は「値表示モード」「グラフモード」「グラフモード（値表示有り）」の3種類あります。
- ※M5StickC Plusの場合は「値表示モード」時に左にトレンド矢印が出ます。（過去5分の平均値より、直近30秒平均値が"高い"か"低い"かを示す。）
- 「グラフモード」「グラフモード（値表示有り）」は過去の測定値の変化グラフになっており、画面下端が400ppmで上端が2000ppmを示します。
- 薄い赤の塗り潰しは、CO2計測値の警告閾値越えを示しています。デフォルトは厚生労働省の換気目安の1000ppmとしております。「閾値」は、設定ファイルの「CO2_RED」の値です。
- グラフの範囲は、M5StickC Plusは240回分（5秒毎測定なので、おおよそ20分間分）、M5StickC無印は160回分（おおよそ13分間分）となります。

![M5StickC_1](https://kitto-yakudatsu.com/wp/wp-content/uploads/2019/11/P1300153-scaled.jpg)

![M5StickC_2](https://kitto-yakudatsu.com/wp/wp-content/uploads/2019/11/P1300156-scaled.jpg)

![M5StickC_3](https://kitto-yakudatsu.com/wp/wp-content/uploads/2019/11/P1300158-scaled.jpg)

![M5StickC_4](https://kitto-yakudatsu.com/wp/wp-content/uploads/2019/11/P1300165-scaled.jpg)

![M5StickC_5](https://kitto-yakudatsu.com/wp/wp-content/uploads/2019/11/P1300166-scaled.jpg)

![M5StickC_5](https://kitto-yakudatsu.com/wp/wp-content/uploads/2019/11/P1300170-scaled.jpg)

<br>

## M5StickC/Plusのボタン操作

- Aボタン（M5ロゴの有るボタン）を押すと画面モードを出来ます。最初は値表示モード、次にグラフモード、グラフモード（値表示有り）に遷移します。
- Bボタン（電源ボタンじゃない方の側面ボタン）を押すと表示が180度回転しますので、設置向きに合わせてお選び下さい。

<br>

# <その他、参考情報>
* HD端子の接続は非推奨としております。（Co2 HATの出荷状態では未接続です）
※M5StickC後期版（電源OFFした際に5V OUTが一緒に落ちるタイプ）では使用できますが、M5StickCの外見だけでは判別付かないので、分かる方のみ使用して下さい。<br>
※尚、Co2 HATのジャンパーピンの処置の変更が必要になる場合もあります。ピンの割り当て方や回路が追える方のみお使い願います。（質問は受け付けかねます）<br>
* その他の情報については[ブログ](https://kitto-yakudatsu.com/archives/7286)をご参照下さい。<br>

<br>

# <アップデート履歴>

## 【2021.10.15】 [test_CO2_Ambient.py] Update!

* 画面UIを刷新。（時計表示を無くし、グラフ表示モードを追加しました。詳しくは上記の＜使い方＞をご参照下さい。）
* Ambient設定が無い場合は、WiFi通信無しでも動く様に修正。
* 他に「MH-Z19B/C」からの応答が9バイト未満になった際に応答不能になるバグを修正。

<br>

## 【2021.06.02】 [test_CO2_Ambient.py] Update! , [CO2_zeropoint.py] Update! , [CO2_zeropointHD.py] add!

* 基板Rev0.2対応。（Rev0.2からUARTピン割当てが変更されました）
* HD端子によるゼロポイントキャリブレーション用サンプルプログラム追加（説明は省きます。MH-Z19B/Cの仕様書を読んで、環境構築も含め、ソースが分かる方だけお使い下さい。）

<br>

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

