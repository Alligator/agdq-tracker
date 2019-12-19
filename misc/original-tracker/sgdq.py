import json
import urllib2
import time
import sys

import lxml.html
from datetime import datetime, timedelta

# get viewers
j = json.load(urllib2.urlopen('https://api.twitch.tv/kraken/streams/speeddemosarchivesda'))
e = json.load(open('/var/www/sgdq.json'))['viewers']
try:
  t = j['stream']['viewers']
except Exception, e:
  sys.exit(0)
e.append((time.time(), t))

# get schedule
h = urllib2.urlopen('http://marathon.speeddemosarchive.com/schedule').read()
html = lxml.html.fromstring(h)
x = html.xpath("//table[@id='runTable']//tbody//tr[not(contains(@id, 'daySplit'))]")
# 7/29/2013 10:50:00
# times are -6 ugh
g = []
for elm in x:
  tm = datetime.strptime(elm.getchildren()[0].text, '%m/%d/%Y %H:%M:%S') + timedelta(hours=7)
  tm = time.mktime(tm.timetuple())
  game = elm.getchildren()[1].text
  g.append([tm, game])

json.dump({'viewers': e, 'games': g}, open('/var/www/sgdq.json', 'w'))