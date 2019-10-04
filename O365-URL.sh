#!/bin/bash

set -u
## set file permission to RW
umask 0111

## suppress curl memory consumption
export NSS_SDB_USE_CACHE=NO

## parameters to upload files via aXAPI 
readonly HOST="localhost"
readonly PARTITION="shared"
readonly TARGET="class-list"
readonly USER="admin"
readonly PASS="a10"
readonly AC_MATCH="ends-with"

## working directory
readonly WORKDIR="/a10data/guest/O365/${PARTITION}"

## parameters to get Office 365 endpoints information
readonly URL="https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7"
readonly LIST="${WORKDIR}/urllist"
readonly PROXY=""
#readonly PROXY="172.16.0.43:3128"

## parameters to find valid execution timing
readonly CURR_TIME=$(date +%H:%M)
readonly BEGIN_TIME="00:00"
readonly END_TIME="23:59"

## select ac match type 
param_check()
{
  if [ "${AC_MATCH}" == "contains" ] || [ "${AC_MATCH}" == "ends-with" ]; then
   :
  else 
   echo "AC_MATCH:${AC_MATCH} isn't valid. It should be 'contains' or 'ends-with'."
   exit 1
  fi
}

## exec schedule
time_check()
{
  if [[ "${CURR_TIME}" < "${BEGIN_TIME}" ]] || [[ "${CURR_TIME}" > "${END_TIME}" ]]; then
   echo "${CURR_TIME} => NO GO"
   exit 0
  else
   echo "${CURR_TIME} => GO" 
  fi
}

## check file dir and move 
dir_check() {
  if [ -d "${WORKDIR}" ]; then
   cd ${WORKDIR} ||  exit 1
  else
   mkdir -p -m 777 ${WORKDIR} ||  exit 1
   cd ${WORKDIR} || exit 1
  fi
}

## get source list and save
get_source() {
  if [ -z "$PROXY" ]; then
   curl -sS -k -m 5 --retry 1 -o ${LIST} "${URL}" || exit 1
  else
   curl -sS -k -m 5 --retry 1  -o ${LIST} "${URL}" -x ${PROXY} || exit 1
  fi
}

## create class-list files  
create_list() {
  ## divide original list into ID based dictionary files  
  if [ -w ${LIST} ]; then
   awk '/{/,/}/' ${LIST} | awk '/{/ {x="dict."++i;}{print > x;}' 
  else
   exit 1
  fi
   
  ## create null files to be updated 
  for route_type in EXP DEF; do
    : >dict.${route_type}
    for key_name in urls ipv4 ipv6; do
     : >o365-${key_name}-${route_type}
    done
  done
   
  ## list file names which "expressRoute" is True ==>> EXP(ress)
  awk '/"expressRoute": tr/ {print FILENAME}' dict.* | while read dict_name; do
   cat "${dict_name}" >>dict.EXP
  done
   
  ## list file names which "expressRoute" is False ==>> DEF(ault)
  awk '/"expressRoute": fa/ {print FILENAME}' dict.* | while read dict_name; do
   cat "${dict_name}" >>dict.DEF
  done
   
  ## create list of urls, ipv4 and ipv6 for both EXP and DEF
  for route_type in EXP DEF; do
   awk '/urls/,/]/' dict.${route_type} | awk ' ! /[\[\]]/' |sed -e 's/^ *\"//' -e 's/\".*//' -e 's/.*\*//' | sort -u >urls.${route_type}
   awk '/\"ips\"/,/]/' dict.${route_type}  | awk '! /[\[\]]/ && /\./' | sed -e "s/^ *\"//"  -e "s/\".*//" |sort -u >ipv4.${route_type}
   awk '/\"ips\"/,/]/' dict.${route_type}  | awk '! /[\[\]]/ && /\:/' | sed -e "s/^ *\"//"  -e "s/\".*//" |sort -u >ipv6.${route_type}
  done
   
  ## check duplicated entries and create lists for those ==>> DUP(licate)
  for key_name in urls ipv4 ipv6; do
   sort -m ${key_name}.EXP ${key_name}.DEF | uniq -d > ${key_name}.DUP
   sort -m ${key_name}.EXP ${key_name}.DUP | uniq -u > o365-${key_name}-EXP
   sort -m ${key_name}.DEF ${key_name}.DUP | uniq -u > o365-${key_name}-DEF
   mv ${key_name}.DUP o365-${key_name}-DUP
  done
   
  ## convert the lists to class-list format
  for route_type in EXP DEF DUP; do
   sed -i -e "s/^/${AC_MATCH} /" o365-urls-${route_type}
   (echo "class-list o365-urls-${route_type} ac file" ; cat o365-urls-${route_type}) > o365-urls-${route_type}.tmp
   mv o365-urls-${route_type}.tmp o365-urls-${route_type}
   for key_name in ipv4 ipv6; do
    (echo "class-list o365-${key_name}-${route_type} ${key_name} file" ; cat o365-${key_name}-${route_type}) > o365-${key_name}-${route_type}.tmp
    mv o365-${key_name}-${route_type}.tmp o365-${key_name}-${route_type} 
   done
  done
   
  ## create json file for class-list import
  for route_type in EXP DEF DUP; do
   for key_name in urls ipv4 ipv6; do
    echo "{\"class-list\": {\"action\": \"import\",\"file\": \"o365-${key_name}-${route_type}\",\"file-handle\": \"o365-${key_name}-${route_type}\"}}" > o365-${key_name}-${route_type}.json
   done
  done
}

## import class-list files
import_list() {
  ## login via aXAPI
  local -r CURL="curl -sS -k -m 4"
  local -r SIGN=$(${CURL} -H "Content-type: application/json" -X POST -d "{\"credentials\": {\"username\": \"$USER\", \"password\": \"$PASS\"}}" https://${HOST}/axapi/v3/auth | awk -F'"' '/\"signature\"/ {print $4}')
  local -r TOKEN="Authorization: A10 ${SIGN}"
   
  ## switch to the partition uses the class-lists
  ${CURL} -H "${TOKEN}" -X POST https://${HOST}/axapi/v3/active-partition/${PARTITION} 
  
  ## import class-lists
  for route_type in EXP DEF DUP; do
   for key_name in urls ipv4 ipv6; do
    ${CURL} -H "${TOKEN}" -H "Content-Type: multipart/form-data" -F json=@o365-${key_name}-${route_type}.json -F file=@o365-${key_name}-${route_type} -X POST https://${HOST}/axapi/v3/file/${TARGET}
    sleep 5
   done
  done    
   
  ## logoff
  ${CURL} -H "${TOKEN}" -X POST https://$HOST/axapi/v3/logoff
}

## clean up created files
cleanup() {
  rm -f dict.*
  rm -f url*
  rm -f ipv*
  rm -f o365*
}

## exec
time_check && param_check && dir_check && cleanup && get_source && create_list && import_list
