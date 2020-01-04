# -*- coding: utf-8 -*-
import json
import time
import requests
import math
import sys
from datetime import datetime
from pprint import pprint

j = json.load(open('PATH TO JSON HERE'))
games = j['games']
total = j['viewers'][-1]
now  = time.time()

before = [x for x in games if x[0] < now]
after = [x for x in games if x[0] >= now]

print(len(before))
print(len(after))

if len(before) == 0:
  # nothing before, not started
  sys.exit(0)

if len(after) == 0:
  # nothing after, finished
  sys.exit(0)

diff = now - before[-1][0]

nextDate = datetime.fromtimestamp(after[0][0])
nowDate = datetime.fromtimestamp(now)
diff = (nextDate - nowDate).total_seconds()
totalMins = math.floor(diff / 60)
hours = int(totalMins / 60)
mins = int(totalMins % 60)
nextMsg = ''
if hours == 1:
  nextMsg = 'in {} hour {} minutes'.format(hours, mins)
elif hours > 1:
  nextMsg = 'in {} hours {} minutes'.format(hours, mins)
else:
  nextMsg = 'in {} minutes'.format(mins)

currentGame = before[-1][1].encode('utf-8')
prevGame = open('/tmp/gdq-prev').read()

if currentGame != prevGame:
  open('/tmp/gdq-prev', 'w').write(currentGame)
  msg = u'current game: {} | next: {} | viewers: {} | total: ${}'.format(before[-1][1], after[0][1], total[1], total[2])
  data = {
    'embeds': [{
      'title': 'SGDQ 2019',
      'url': 'https://www.twitch.tv/gamesdonequick',
      'fields': [
        {
          'name': 'Current Game',
          'value': before[-1][1],
        },
        {
          'name': 'Next Game',
          'value': '{}, {}'.format(after[0][1], nextMsg),
        },
        {
          'name': 'Viewers',
          'value': str(total[1]),
          'inline': True,
        },
        {
          'name': 'Donation Total',
          'value': '$' + str(total[2]),
          'inline': True,
        },
      ],
    }],
  }
  url = 'DISCORD WEBHOOK HERE'
  pprint(data)
  resp = requests.post(url, json=data)
  print(resp)

