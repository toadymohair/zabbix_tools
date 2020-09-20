#!/bin/bash

# bloadcastingType
B_TYPE=$1

# serviceId
S_ID=$2

URL_GET_CHANNEL_LIST="http://192.168.0.104:64210/status/channelListGet?broadcastingType=$B_TYPE"

CHANNEL_INFO=`curl -s $URL_GET_CHANNEL_LIST | jq '.channel[] | select(.serviceId=='$S_ID')'`

# networkId
N_ID=`echo $CHANNEL_INFO | jq '.networkId'`

# transportStreamId
TS_ID=`echo $CHANNEL_INFO | jq '.transportStreamId'`

URL_GET_LIVE_INFO="http://192.168.0.104:64210/status/channelInfoGet2?networkId=$N_ID&transportStreamId=$TS_ID&serviceId=$S_ID&withDescriptionLong=0"

LIVE_INFO=`curl -s $URL_GET_LIVE_INFO | jq '.'`

echo $LIVE_INFO
