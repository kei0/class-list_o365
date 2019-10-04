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
- o365-urls-EXP
  - urlsでexpressRoute true
- o365-urls-DEF
  - urlsでexpressRoute false
- o365-urls-DUP   
  - urlsでexpressRoute true/false どちらにも存在
- o365-ipv4-EXP
  - ipv4でexpressRoute true  
- o365-ipv4-DEF
  - ipv4でexpressRoute false
- o365-ipv4-DUP
  - ipv4でexpressRoute true/false どちらにも存在
- o365-ipv6-EXP
  - ipv6でexpressRoute true  
- o365-ipv6-DEF
  - ipv6でexpressRoute false
- o365-ipv6-DUP
  - ipv6でexpressRoute true/false どちらにも存在
  
## 動作確認済み ACOSバージョン
```
4.1.4-p2、4.1.1-p9、4.1.4-GR1-p1
```

## Step 1. ダウンロードしたサンプルスクリプトを編集 (必要に応じて） 
- class-listを利用するパーティションを指定
```
readonly PARTITION="shared"
```
- ACOS管理ユーザパスワードの設定
```
readonly USER="admin"
readonly PASS="a10"
```
- スクリプトを実行する時間帯の変更 
```
readonly BEGIN_TIME="00:00"
readonly END_TIME="23:59"
 -> 24時間表記で、時:分の形で指定する（一桁は頭に0をつけ、二桁表示にする）
 -> 少なくとも10分間（ヘルスチェック3回分）は確保する
 -> 意味なく長時間可動させない（メモリリソース消費させない）
 -> 動作確認する場合は show clock で時刻をみておく
 -> 必要あればntp serverで時刻合わせておく
 -> 日またぎ（例: BEGIN_TIME 23:00,END_TIME 01:00）は設定しない
```
- ACマッチタイプの指定
```
readonly AC_MATCH="ends-with"
 -> urlsの場合、先頭からワイルドカード"*"の部分まで削除しているので、下記の指定を想定する
 -> host 比較の場合は ends-with か contains
 ｰ> url 比較の場合は contains
```
- Office 365リスト採取の際にプロキシが必要な場合
```
readonly PROXY=""
 -> curlのプロキシ指定 例 172.16.0.43:3128 で設定
```
- その他はそのまま使用

## Step 2. シェアードパーティションでの準備
- ACOSにスクリプトをインポート
```
import health-external O365-URL.sh overwrite use-mgmt-port scp://user:password@<HOSTNAME or IP_ADDRESS>/<path>/O365-URL.sh
```
- インターネットとDNSの設定

```
! 例
!
ip dns primary <IP_ADDRESS>
!
ip route 0.0.0.0 /0 <IP_ADDRESS>
!
ntp server <FQDN|IP_ADDRESS>
```
- External Health Monitorの設定
```
! 例
!
health monitor o365 
  retry 1 
  interval 180 timeout 80 
  !間隔・タイムアウトはこれより短くしない!
  method external program O365-URL.sh
!
slb server s1 127.0.0.1 
  health-check o365 
!
```
- 実行状況の確認
```
 ACOS# show health stat
 -> チェックスクリプトが一度成功するとUP
 
 ACOS# show health external-log
 −> 成功の場合
 実行時
 16:27 => GO
 抑止時 
 17:30 => NO GO

 -> 失敗の場合
 下記のようなエラー(例)が表示
 curl: (6) Couldn't resolve host 'endpoints.office.com'
 curl: (7) Failed to connect to 13.91.37.26: Network is unreachable
 
 ACOS# show log
  -> アクセスログがあるか確認
     なお、4.1.4であれば
	 show log | in PBSLB
	 で下記のようなログ
	 [PBSLB]:Classlist <o365-ipv6-DUP>: loaded into AX.

 ACOS# show audit
  -> aXAPIを叩いた履歴を確認
```

## Step 3. クラスリストを利用するパーティションにて、policy-templateの設定（シェアードパーティションまたはプライベートパーティション）
- クラスリストの確認
```
 ACOS# show class-list
 -> 9つのファイルが作成されていること
 例)
 TH17-25[p1]#sh class-list 
 Name                     Type                     IP       Subnet   DNS      String   Location
 o365-urls-EXP            ac                       0        0        0        81       file    
 o365-ipv4-EXP            ipv4                     105      136      0        0        file    
 o365-ipv6-EXP            ipv6                     122      72       0        0        file    
 o365-urls-DEF            ac                       0        0        0        345      file    
 o365-ipv4-DEF            ipv4                     70       3        0        0        file    
 o365-ipv6-DEF            ipv6                     90       7        0        0        file    
 o365-urls-DUP            ac                       0        0        0        1        file    
 o365-ipv4-DUP            ipv4                     4        1        0        0        file    
 o365-ipv6-DUP            ipv6                     26       0        0        0        file    
 Total: 9
 TH17-25[p1]#
 
 ACOS# show class-list <リスト名>
 -> エントリーの確認
 ```
 
 - テンプレートへの反映
 ```
 ! 例
!
slb template policy p 
  forward-policy 
    action drop 
      drop 
    source s 
      match-any 
      destination class-list o365-urls-EXP action drop host priority 1 
      destination class-list o365-urls-DEF action drop host priority 2 
      destination class-list o365-urls-DUP action drop host priority 3 
      destination class-list o365-ipv4-EXP action drop host priority 4 
      destination class-list o365-ipv4-DEF action drop host priority 5 
      destination class-list o365-ipv4-DUP action drop host priority 6 

!

# ipv6 クラスリストは透過Proxy時に利用可能
 ```
