#!/bin/bash

. ../config.sh

curl -s -X POST "https://id.twitch.tv/oauth2/token?client_id=$twitch_client_id&client_secret=$twitch_client_secret&grant_type=client_credentials" | jq
