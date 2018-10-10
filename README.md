# class-list_o365
## 概要
- "Office 365 IP Address and URL Web service"より、"urls"および"ips"の情報をすべて抽出。
- url/ipそれぞれについて"expressRoute"のtrue/falseに応じてclass-list化。
- 同じurl/ipが"expressRoute"のtrue/falseどちらにも属する場合は、別のclass-listを設ける。
- urlがアスタリスク(\*)を含む場合はアスタリスク以前を削除。 \*.x.y.z → .x.y.z
- Class-list作成以外の基本的な動作概念については以前の「Office365用class-list自動化Shellスクリプト」を踏襲しているので、詳細はそちらを参照。

## Office 365 IP Address and URL
[Office 365 Endpoints for proxy servers](https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7)

## 作成される class-list
- o365-url 
  - url * expressRoute false
- o365-urlER
  - url * expressRoute true
- o365-urlDUP
  - url * expressRoute 双方に存在 (DUPlicate)
- o365-ipv4
  - ip(v4) * expressRoute false
- o365-ipv4ER
  - ip(v4) * expressRoute true
- o365-ipv4DUP
  - ip(v4) * expressRoute 双方に存在 (DUPlicate)
- o365-ipv6
  - ip(v6) * expressRoute false
- o365-ipv6ER
  - ip(v6) * expressRoute true
- o365-ipv6DUP
  - ip(v6) * expressRoute 双方に存在 (DUPlicate)
  
## 動作確認済み ACOSバージョン
```
4.1.4-p2 （4.1.1-p9では動作しません）
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
  interval 180 timeout 80
  !上記のinterval/timeoutはこれより短くしません
  method external program clist.o365.py 
!
slb server me 127.0.0.1 
  health-check o365 
!
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
