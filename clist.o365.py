#!/usr/bin/env python

import os
#os.environ['NO_PROXY'] = 'endpoints.office.com'
os.chdir('/a10data/tmp')
os.umask(0o111)

import datetime
import requests
import json
import re
from itertools import chain
from time import sleep

def create_list():
 url="https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7"
 r=requests.get(url, verify=False, timeout=3)
 l=r.json()
 
 url_keys=['urls']
 
 l_url=[d.get(url_key) for url_key in url_keys for d in l if d.get(url_key) and not d['expressRoute']]
 l_url=list(chain.from_iterable(l_url))
 set_l_url=set(l_url)   
 
 l_url_e=[d.get(url_key) for url_key in url_keys for d in l if d.get(url_key) and d['expressRoute']]
 l_url_e=list(chain.from_iterable(l_url_e))
 set_l_url_e=set(l_url_e)      
 
 set_l_url_d=set_l_url_e & set_l_url
 set_l_url=set_l_url - set_l_url_d
 set_l_url_e=set_l_url_e - set_l_url_d
 
 l_url=list(set_l_url)    
 l_url_e=list(set_l_url_e)
 l_url_d=list(set_l_url_d)
 
 match='ends-with '
 ftype='ac'
 fprod='o365-'
   
 fmod='url'
 fmod_e='urlER'
 fmod_d='urlDUP'
 fname=fprod+fmod
 fname_e=fprod+fmod_e
 fname_d=fprod+fmod_d
 fheader='class-list'+' '+fname+' '+ftype+' '+'file'
 fheader_e='class-list'+' '+fname_e+' '+ftype+' '+'file'
 fheader_d='class-list'+' '+fname_d+' '+ftype+' '+'file'
 with open(fname,'w') as f:
  f.write(fheader)
  f.write('\n')
  for u in l_url:
   u=re.sub(r'^.*\*','',u)
   u=match+u
   f.write(u)
   f.write('\n')

 with open(fname_e,'w') as f:
  f.write(fheader_e)
  f.write('\n')
  for u in l_url_e:
   u=re.sub(r'^.*\*','',u)
   u=match+u
   f.write(u)
   f.write('\n')
  
 with open(fname_d,'w') as f:
  f.write(fheader_d)
  f.write('\n')
  for u in l_url_d:
   u=re.sub(r'^.*\*','',u)
   u=match+u
   f.write(u)
   f.write('\n')
  
 ip_keys=['ips']
 l_ip=[d.get(ip_key) for ip_key in ip_keys for d in l if d.get(ip_key) and not d['expressRoute']]  
 l_ip=list(chain.from_iterable(l_ip))
 l_v4=[a for a in l_ip if '.' in a]
 l_v6=[a for a in l_ip if ':' in a]
  
 l_ip_e=[d.get(ip_key) for ip_key in ip_keys for d in l if d.get(ip_key) and d['expressRoute']]
 l_ip_e=list(chain.from_iterable(l_ip_e))
 l_v4_e=[a for a in l_ip_e if '.' in a]
 l_v6_e=[a for a in l_ip_e if ':' in a]
  
 set_l_v4=set(l_v4)
 set_l_v4_e=set(l_v4_e)
 
 set_l_v4_d=set_l_v4_e & set_l_v4
 set_l_v4=set_l_v4 - set_l_v4_d
 set_l_v4_e=set_l_v4_e - set_l_v4_d
  
 l_v4=list(set_l_v4)
 l_v4_e=list(set_l_v4_e)
 l_v4_d=list(set_l_v4_d)
 
 ftype='ipv4'
 fprod='o365-'
 fmod='ipv4'
 fmod_e='ipv4ER'
 fmod_d='ipv4DUP'
  
 fname=fprod+fmod
 fname_e=fprod+fmod_e
 fname_d=fprod+fmod_d
 fheader='class-list'+' '+fname+' '+ftype+' '+'file'
 fheader_e='class-list'+' '+fname_e+' '+ftype+' '+'file'
 fheader_d='class-list'+' '+fname_d+' '+ftype+' '+'file'
 with open(fname,'w') as f:
  f.write(fheader)
  f.write('\n')
  for u in l_v4: 
   f.write(u)
   f.write('\n')
  
 with open(fname_e,'w') as f:
  f.write(fheader_e)
  f.write('\n')
  for u in l_v4_e:
   f.write(u)
   f.write('\n')
   
 with open(fname_d,'w') as f:
  f.write(fheader_d)
  f.write('\n')
  for u in l_v4_d:
   f.write(u)
   f.write('\n')
  
 set_l_v6=set(l_v6)
 set_l_v6_e=set(l_v6_e)
  
 set_l_v6_d=set_l_v6_e & set_l_v6
 set_l_v6=set_l_v6 - set_l_v6_d
 set_l_v6_e=set_l_v6_e - set_l_v6_d
 
 l_v6=list(set_l_v6)
 l_v6_e=list(set_l_v6_e)
 l_v6_d=list(set_l_v6_d)
  
 ftype='ipv6'
 fprod='o365-'
 fmod='ipv6'
 fmod_e='ipv6ER'
 fmod_d='ipv6DUP'
 
 fname=fprod+fmod
 fname_e=fprod+fmod_e
 fname_d=fprod+fmod_d
 fheader='class-list'+' '+fname+' '+ftype+' '+'file'
 fheader_e='class-list'+' '+fname_e+' '+ftype+' '+'file'
 fheader_d='class-list'+' '+fname_d+' '+ftype+' '+'file'
 with open(fname,'w') as f:
  f.write(fheader)
  f.write('\n')
  for u in l_v6: 
   f.write(u)
   f.write('\n')
  
 with open(fname_e,'w') as f:
  f.write(fheader_e)
  f.write('\n')
  for u in l_v6_e:
   f.write(u)
   f.write('\n')
  
 with open(fname_d,'w') as f:
  f.write(fheader_d)
  f.write('\n')
  for u in l_v6_d:
   f.write(u)
   f.write('\n')

def import_list():

 host='127.0.0.1'
 pdata={'credentials':{'username':'admin','password':'a10'}}
 hdr={'content-type': 'application/json'}
 prot='https://'
 url =prot+host+'/axapi/v3/auth'
 r=requests.post(url, json=pdata, headers=hdr, verify=False, timeout=3)
 d=r.json()
 sign ='A10 '+d['authresponse']['signature']
 hdr['authorization']=sign
 
 part='shared'
 call_url=prot+host+'/axapi/v3/active-partition/'+part
 call=requests.post(call_url, headers=hdr, verify=False, timeout=3)
 
 hdr2={}
 hdr2['authorization']=sign
 call_url=prot+host+'/axapi/v3/file/class-list'
 
 types=['url','urlER','urlDUP','ipv4','ipv4ER','ipv4DUP','ipv6','ipv6ER','ipv6DUP']
 for type in types:
  jsn='''{{
  "class-list":{{
  "action":"import",
  "file":"o365-{x}",
  "file-handle":"o365-{x}"
  }}
  }}'''.format(x=type).strip()
  fname='o365-'+type
  with open(fname) as f:
   f=f.read()
   print(f)
   files={
    'json': (type,jsn,'application/octet-stream'), 
    'file': (fname,f,'application/octet-stream')
   }
  call=requests.post(call_url, headers=hdr2, files=files, verify=False, timeout=3)
  sleep(5)
  
 logout_url = prot+host+'/axapi/v3/logoff'
 logout = requests.post(logout_url, headers=hdr, verify=False, timeout=3)

now=datetime.datetime.now()
hour=01
minm=01
maxm=10
if now.hour == hour and minm < now.minute < maxm:
 print(str(now.hour)+str(now.minute)+' GO')
 create_list()
 import_list()
else:
 print(str(now.hour)+str(now.minute)+' not now')
