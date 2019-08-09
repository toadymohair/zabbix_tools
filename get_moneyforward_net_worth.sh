#!/bin/bash

zabbix_server_host=$1
zabbix_monitor_host="MoneyForward"
zabbix_monitor_item="networth"

login_cookie='/root/cookies/moneyforward_login.cookie'
session_cookie='/root/cookies/moneyforward_session.cookie'

username=`cat ~/login/moneyforward.com.user`
password=`openssl rsautl -decrypt -inkey ~/.ssh/id_rsa -in ~/login/moneyforward.com.passwd`

user_agent="Mozilla/5.0"

readonly program=$(basename $0)

function print_usage_and_exit() {
  echo >&2 "Usage: ${program} ZABBIX_SERVER_HOSTNAME"
  exit 1
}

if [ $# -ne 1 ]; then
  print_usage_and_exit
fi

function get_at(){
  row_data=`curl -s -c $login_cookie 'https://moneyforward.com/users/sign_in' -A $user_agent`

  echo $row_data | grep authenticity_token | awk '{
    match($0, "authenticity_token.*/>")
    match1 = substr($0, RSTART, RLENGTH)
    match(match1, "content=[^>]*>")
    match2 = substr(match1, RSTART, RLENGTH)
    match(match2, "\".*\"")
    at = substr(match2, RSTART+1, RLENGTH-2)
    print at
    }
  '
}

function login(){
  at=`get_at`

  curl \
  -A $user_agent \
  -H 'Referer:https://moneyforward.com/users/sign_in' \
  -H 'Accept:text/html, application/xhtml+xml, */*' \
  -H 'Content-Type:application/x-www-form-urlencoded' \
  -X POST \
  --data-urlencode 'authenticity_token='$at \
  --data-urlencode 'sign_in_session_service[email]='$username \
  --data-urlencode 'sign_in_session_service[password]='$password \
  --dump-header - \
  -b $login_cookie \
  -c $session_cookie \
  -s \
  https://moneyforward.com/session
}

function get_net_worth(){
  row_data=`curl -s -A $user_agent -b $session_cookie https://moneyforward.com/bs/balance_sheet | awk '
    BEGIN{FS="\n"; RS=">"}
    /純資産.*円/{
      print $3
    }'`
  echo $row_data | sed -e 's/,//g' | sed -e 's/円//g'
}

login > /dev/null

zabbix_sender -z $zabbix_server_host -s $zabbix_monitor_host -k $zabbix_monitor_item -o `get_net_worth`
