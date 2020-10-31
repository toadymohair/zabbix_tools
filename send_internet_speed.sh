#!/bin/bash

zabbix_server_host="cmn.tmhr.work"
zabbix_monitor_host="RP01"
zabbix_monitor_item_ul="sptest_ul"
zabbix_monitor_item_dl="sptest_dl"

SP_TEST_RESULT=`speedtest -L | grep "OPEN Project" | awk '{print $1}' | xargs speedtest -f json -s`

#echo $SP_TEST_RESULT

dl_speed=`echo $SP_TEST_RESULT | jq .download.bandwidth`
ul_speed=`echo $SP_TEST_RESULT | jq .upload.bandwidth`
result_url=`echo $SP_TEST_RESULT | jq .result.url`

#echo "dl: $dl_speed"
#echo "ul: $ul_speed"
#echo "result: $result_url"

zabbix_sender -z $zabbix_server_host -s $zabbix_monitor_host -k $zabbix_monitor_item_dl -o $dl_speed

zabbix_sender -z $zabbix_server_host -s $zabbix_monitor_host -k $zabbix_monitor_item_ul -o $ul_speed
