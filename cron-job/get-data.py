import json
import time
import sys
import requests
import re
import configparser

import lxml.html
from datetime import datetime, timedelta
from dateutil import parser

from pprint import pprint

filename = '../web/MARATHON_NAME.json'

# marathon start and end times go here, so I don't have to worry about turning
# the cron job on or off at the right time
current_time = time.time()
start_date = parser.parse('START_DATE')
end_date = parser.parse('END_DATE')
if 'force' not in sys.argv and (datetime.utcnow() < start_date or datetime.utcnow() > end_date):
  sys.exit(0)

try:
  current_stats = json.load(open(filename))
except IOError as e:
  current_stats = { 'viewers': [], 'games': [] }

# get viewers
for i in range(3):
  try:
    headers = {
      'Client-ID': 'TWITCH_CLIENT_ID',
      'Authorization': 'Bearer TWITCH_ACCESS_TOKEN',
    }
    j = json.loads(requests.get('https://api.twitch.tv/helix/streams?user_id=22510310', headers=headers, verify=True, timeout=10.0).text)
    if len(j['data']) == 0:
        t = None
        break;
    t = j['data'][0]['viewer_count']
    break
  except Exception as e:
    # write out a null
    sys.stderr.write('viewers ' + str(e) + '\n')
    t = None

# get donations
try:
  j = json.loads(requests.get('https://gamesdonequick.com/tracker/event/MARATHON_NAME_FULL?json').text)
  dn = float(j['agg']['amount'])
except Exception as e:
  sys.stderr.write('donations' + str(e) + '\n')
  dn = None

current_stats['viewers'].append((current_time, t, dn))

# get schedule
try:
  resp = requests.get('https://gamesdonequick.com/tracker/api/v2/events/MARATHON_ID/runs/')
  resp.raise_for_status()
  j = json.loads(resp.text)

  games = []
  for run in j['results']:
    if run['type'] != 'speedrun':
      continue
    name = run['display_name']
    tm = parser.parse(run['starttime']).timestamp()
    runners = ', '.join(r['name'] for r in run['runners'])
    category = run['category']
    games.append([tm, name, runners, category])

  if len(games) == 0:
    raise Exception('no games, reverting')
  current_stats['games'] = games
except Exception as e:
  # on error don't change the games
  sys.stderr.write('games ' + str(e) + '\n')
  pass

json.dump(current_stats, open(filename, 'w'))
