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
if datetime.utcnow() < start_date or datetime.utcnow() > end_date:
  sys.exit(0)

try:
  current_stats = json.load(open(filename))
except IOError as e:
  current_stats = { 'viewers': [], 'games': [] }

# get viewers
for i in range(3):
  try:
    headers = { 'Client-ID': 'TWITCH_KEY' }
    j = json.loads(requests.get('https://api.twitch.tv/helix/streams?user_login=gamesdonequick', headers=headers, verify=True, timeout=10.0).text)
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
  h = requests.get('http://gamesdonequick.com/schedule', timeout=15.0).text
  html = lxml.html.fromstring(h)
  x = html.xpath("//table[@id='runTable']/tbody/tr[not(contains(@class, 'day-split')) and not(contains(@class, 'second-row'))]")
  # 7/29/2013 10:50:00
  # times are -5 ugh
  g = []
  for elm in x:
    # tm = datetime.strptime(elm.getchildren()[0].text, '%Y-%m-%dT%H:%M:%SZ')
    tm = parser.parse(elm.getchildren()[0].text)
    tm = time.mktime(tm.timetuple())
    game = elm.getchildren()[1].text
    runners = elm.getchildren()[2].text
    g.append([tm, game, runners])
  if len(g) == 0:
    raise Exception('no games, reverting')
  current_stats['games'] = g
except Exception as e:
  # on error don't change the games
  sys.stderr.write('games\n' + str(e))
  pass

json.dump(current_stats, open(filename, 'w'))
