#!/bin/bash
set -e

. ./config.sh

echo "creating directory $marathon_name"
mkdir $marathon_name

echo "copying files"
cp -r cron-job $marathon_name
cp -r web $marathon_name

cd $marathon_name

echo "setting stuff up for $marathon_nice_name"

echo "replacing variables in cron-job/get-data.py"
sed -i \
  -e "s/MARATHON_NAME_FULL/$marathon_name_full/g" \
  -e "s/MARATHON_NAME/$marathon_name/g" \
  -e "s/START_DATE/$marathon_start_date/g" \
  -e "s/END_DATE/$marathon_end_date/g" \
  -e "s/TWITCH_CLIENT_ID/$twitch_client_id/g" \
  -e "s/TWITCH_ACCESS_TOKEN/$twitch_access_token/g" \
  ./cron-job/get-data.py

echo "replacing variables in web/index.js"
sed -i \
  -e "s/MARATHON_NAME_FULL/$marathon_name_full/g" \
  -e "s/MARATHON_NAME/$marathon_name/g" \
  -e "s/MARATHON_SHORT_NAME/$marathon_short_name/g" \
  -e "s/MARATHON_NICE_NAME/$marathon_nice_name/g" \
  -e "s/MARATHON_YEAR/$marathon_year/g" \
  ./web/index.html

echo "replacing variables in web/agdq.d3.js"
sed -i \
  -e "s/MARATHON_NAME/$marathon_name/g" \
  ./web/agdq.d3.js

echo "setting up pipenv"
cd cron-job
pipenv install
