# class-list_o365
## 概要
- Office 365のURLソースより、url/ipv4の情報をすべて抽出。
- url/ipv4それぞれについてExpress Routeの真/偽に応じてclass-list化。
- 同じurl/ipv4がExpress Routeの真/偽どちらにも属する場合は、別のclass-listを設ける。
- urlがアスタリスク(\*)を含む場合はアスタリスク以前を削除。 \*.x.y.z → .x.y.z

## Office 365 URL ソース
[Office 365 Endpoints for proxy servers](https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7)

## 作成される class-list
- o365-url 
  - url情報 * Express Route偽
- o365-urlER
  - url情報 * Express Route真
- o365-urlDUP
  - url情報 * Express Route真/偽 双方に存在
- o365-ipv4
  - IPv4情報 * Express Route偽
- o365-ipv4ER
  - IPv4情報 * Express Route真
- o365-ipv4DUP
  - IPv4情報 * Express Route真/偽 双方に存在

## 動作確認済み ACOSバージョン
```
4.1.4-p1, 4.1.1-p8
```

## Step 1. ダウンロードしたサンプルスクリプトを編集 (必要に応じて） 
- デフォルトユーザ名とパスワード（aXAPI実行ユーザなど環境に応じて変更）
```
pdata={'credentials':{'username':'admin','password':'a10'}}
```
- 実行スケジュール（下記の例では13時10−20分の間であれば実行）
```
hour=13
minm=10
maxm=20
```

## Step 2. ACOSのインターネット接続設定 (経路と名前解決)
```
! eg. data interface
!
ip dns primary <IP_ADDRESS>
!
ip route 0.0.0.0 /0 <IP_ADDRESS>
!
```

## Step 3. ACOSにスクリプトをインポート
```
import health-external clist.o365.py overwrite use-mgmt-port scp://user:password@<HOSTNAME or IP_ADDRESS>/<path>/clist.o365.py
```

## Step 4. ACOSでスクリプトを実行（External Health Monitorの利用）
```
!
health monitor o365 
  retry 1 
  interval 180 timeout 60 
  method external program clist.o365.py 
!
slb server me 127.0.0.1 
  health-check o365 
!
```

## Option. non-rootでの実行 (4.1.4のみ)
```
health external privileged disable 
```

## 確認事項
- local clock（スクリプトに定義されている実行時間と筐体時間の比較）
```
show clock
```

- file（スクリプトファイルの表示）
```
show health external clist.o365.py  
```

- log（実行ログの確認）
```
show health external-log
show log
show audit
```

- config, stat（コンフィグ・ステータスの確認）
```
show health monitor | include o365         
show health stat | include o365
```

- edit script（スクリプトの編集）
```
from GUI
ADC > Health Monitors > External Programs > clist.o365.py > Update
```

## Step 5. ファイルの生成を確認後、テンプレートに当てはめる
```
! policy config sample
!
slb template policy o365 
  forward-policy 
    action er 
      forward-to-internet er 
    action gw 
      forward-to-internet gw 
    source s 
      destination class-list o365-ipv4 action gw ip priority 94 
      destination class-list o365-ipv4DUP action gw ip priority 95 
      destination class-list o365-ipv4ER action er ip priority 96 
      destination class-list o365-url action gw host priority 97 
      destination class-list o365-urlDUP action gw host priority 98 
      destination class-list o365-urlER action er host priority 99 
!
```
