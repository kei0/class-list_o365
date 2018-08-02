# class-list_o365
## origin (json file @MS)
[Office 365 Endpoints for proxy servers](https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7)

## class-lists generated
- o365-url 
  - URLs * ER False
- o365-urlER
  - URLs * ER True
- o365-urlDUP
  - URLs * ER True/False Duplicate
- o365-ipv4
  - IPv4 * ER False
- o365-ipv4ER
  - IPv4 * ER True
- o365-ipv4DUP
  - IPv4 * ER True/False Duplicate

## versions tested
```
4.1.4-p1, 4.1.1-p8
```

## prerequisites (edit the script as needed) 
- default username, password
```
pdata={'credentials':{'username':'admin','password':'a10'}}
```
- update schedule
```
hour=13
minm=10
maxm=20
```

## prerequisites (internet connection)
```
! eg. data interface
!
ip dns primary <IP_ADDRESS>
!
ip route 0.0.0.0 /0 <IP_ADDRESS>
!
```

## import script
```
import health-external clist.o365.py overwrite use-mgmt-port scp://user:password@<HOSTNAME or IP_ADDRESS>/<path>/clist.o365.py
```

## execute script
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

## run as non-root (for 4.1.4 only)
```
health external privileged disable 
```

## check
- local clock
```
show clock
```

- file
```
show health external clist.o365.py  
```

- log
```
show health external-log
show log
show audit
```

- config, stat
```
show health monitor | include o365         
show health stat | include o365
```

- edit script
```
from GUI
ADC > Health Monitors > External Programs > clist.o365.py > Update
```

## bind 
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
