#!/bin/bash

URL_GET_CLIENT_LIST="http://192.168.0.104:64210/status/dtcpipClientListGet"
URL_GET_RECORDED_LIST="http://192.168.0.104:64220/recorded/titleListGet?searchCriteria=0&filter=0&startingIndex=0&requestedCount=0&sortCriteria=0&withDescriptionLong=0&withUserData=0"
LAST_ID_FILE=`dirname $0`/data/`basename $0`.list

# 視聴中の番組IDを取得
WATCH_ID=`curl -s $URL_GET_CLIENT_LIST | jq -Mr '.client[].content.id' 2>/dev/null`
curl -s $URL_GET_CLIENT_LIST | jq '.'
curl -s $URL_GET_CLIENT_LIST | jq -Mr '.client[].content.id'

# 録画済み番組のリストを取得
RECORDED_LIST=`curl -s $URL_GET_RECORDED_LIST`


# 録画リストから、IDが一致する番組情報を取得
function get_title_json(){

	# IDリストファイルを配列に格納
	last_id_list=(`cat $LAST_ID_FILE | xargs`)

	for id in $WATCH_ID; do
		if ! `echo ${last_id_list[@]} | grep -q "$id"` ; then
			echo $RECORDED_LIST | jq -Mr '.item[] | select(.id=="'$id'") | { id: .id, title: .title, desc: .description }'
		fi
	done
}


# 以降のループ処理のため、JSONの番組情報を配列に変換
PLAYING_LIST=`get_title_json | jq -s '.'`

LEN=`echo $PLAYING_LIST | jq length`

if [ $LEN -ge 0 ]; then
	for i in $(seq 0 $(($LEN - 1))); do
		echo $PLAYING_LIST | jq -Mr '.['$i'].title'
		echo -e "\t" `echo $PLAYING_LIST | jq -Mr '.['$i'].desc'`
	done
fi

# : > $LAST_ID_FILE


echo $WATCH_ID > $LAST_ID_FILE



