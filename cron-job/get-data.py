import json
import time
import sys
import requests
import re

import lxml.html
from datetime import datetime, timedelta
from dateutil import parser

from pprint import pprint

MARATHON_NAME = 'gdq-test'
filename = '/var/www/{0}/{0}.json'.format(MARATHON_NAME)

current_time = time.time()

# marathon start and end times go here, so I don't have to worry about turning
# the cron job on or off at the right time
start_date = datetime(2019, 6, 23, 16, 20)
end_date = datetime(2019, 6, 30, 12, 0)
if datetime.utcnow() < start_date or datetime.utcnow() > end_date:
  sys.exit(0)

try:
  current_stats = json.load(open(filename))
except IOError as e:
  current_stats = { 'viewers': [], 'games': [] }

# get viewers
for i in range(3):
  headers = { 'Client-ID': 'KEY_GOES_HERE' }
  j = json.loads(requests.get('https://api.twitch.tv/kraken/streams/gamesdonequick', headers=headers, verify=True, timeout=10.0).text)
  try:
    t = j['stream']['viewers']
    break
  except Exception as e:
    # write out a null
    sys.stderr.write('viewers\n' + str(e))
    t = None

# get donations
try:
  j = json.loads(requests.get('https://gamesdonequick.com/tracker/index/{}?json'.format(MARATHON_NAME)).text)
  dn = float(j['agg']['amount'])
except Exception as e:
  sys.stderr.write('donations\n' + str(e))
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
