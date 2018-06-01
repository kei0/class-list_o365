# class-list_o365
■414p1
18-25#sh ver | in Ad
          64-bit Advanced Core OS (ACOS) version 4.1.4-P1, build 69 (Apr-26-2018,19:02)
18-25#

■事前 route & dns
18-25#sh run ip dns
!Section configuration: 30 bytes        
!
ip dns primary 172.17.0.59 
!
18-25#sh run ip route
!Section configuration: 35 bytes        
!
ip route 0.0.0.0 /0 172.16.0.48 
!
18-25#

■インポート
18-25#import health-external clist.o365.py overwrite use-mgmt-port scp://10.200.27.70/Users/koyama/Downloads/clist.o365.py
File clist.o365.py already exists in the system.
Done.
Overwriting existing file clist.o365.py.
18-25#

■コンフィグ

18-25(config)#health external privileged disable 
The external health monitor scripts will be run as non-root.
18-25(config)#
18-25#sh run health
 
18-25#sh run health monitor 
!Section configuration: 102 bytes       
!
health monitor o365 
  retry 1 
  interval 180 timeout 60 
  method external program clist.o365.py 
!
18-25#sh run slb server me
!Section configuration: 48 bytes        
!
slb server me 127.0.0.1 
  health-check o365 
!
18-25#

■確認
18-25#sh health stat 
18-25#sh health external-log
18-25#sh log
18-25#sh audit 

