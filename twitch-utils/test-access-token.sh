#!/bin/bash
set -e

login="$1"

echo "fetching $login"

. ../config.sh

user_id=$(curl -s\
  "https://api.twitch.tv/helix/users?login=$login"\
  -H "Client-ID: $twitch_client_id"\
  -H "Authorization: Bearer $twitch_access_token"\
  | jq -j '.data[0].id')

curl -s\
  "https://api.twitch.tv/helix/streams?user_id=$user_id"\
  -H "Client-ID: $twitch_client_id"\
  -H "Authorization: Bearer $twitch_access_token"\
  | jq '.data[0]'
