#!/bin/bash
set -e

var_unset=0
check_var() {
  val=$(eval "echo \${$1}")
  if [ -z "$val" ]; then
    echo "$1 unset!"
    var_unset=1
  fi
}

. ./config.sh

check_var "marathon_name"
check_var "marathon_name_full"
check_var "marathon_nice_name"
check_var "marathon_short_name"
check_var "marathon_start_date"
check_var "marathon_end_date"
check_var "marathon_year"
check_var "marathon_id"
check_var "twitch_client_id"
check_var "twitch_access_token"

if [ "$var_unset" == "1" ]; then
  echo "variables unset, exiting"
  exit 1
fi

if [ -d "${marathon_name}" ]; then
  echo "directory already exists, exiting"
  exit 1
fi

echo "creating directory $marathon_name"
mkdir $marathon_name

echo "copying files"
cp -r cron-job $marathon_name
cp -r web $marathon_name

cd $marathon_name
tracker_root=$(pwd)

echo "setting stuff up for $marathon_nice_name"

echo "replacing variables in cron-job/get-data.py"
sed -i \
  -e "s/MARATHON_NAME_FULL/$marathon_name_full/g" \
  -e "s/MARATHON_NAME/$marathon_name/g" \
  -e "s/START_DATE/$marathon_start_date/g" \
  -e "s/END_DATE/$marathon_end_date/g" \
  -e "s/MARATHON_ID/$marathon_id/g" \
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

echo "done!"

echo "cron jobs:"
echo "  * * * * * cd $tracker_root/cron-job/ && /home/alligator/.local/bin/pipenv run python get-data.py"
echo "  */10 * * * * sleep 5; cp $tracker_root/web/$marathon_name.json $tracker_root/backup/\`date +\%FT\%T\`.json"
echo "  * * * * * python $tracker_root/gdq-announce.py"
