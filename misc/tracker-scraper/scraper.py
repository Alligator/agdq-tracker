import time
import json
import sys
from datetime import datetime
from pprint import pprint
from multiprocessing.pool import ThreadPool

import lxml.html
import requests

url_fmt = 'https://gamesdonequick.com/tracker/donations/agdq2020{}'
time_fmt = '%m/%d/%Y %H:%M:%S +0000'

data = []

# fetch the number of pages
src =  requests.get('https://gamesdonequick.com/tracker/donations/12').text
html = lxml.html.fromstring(src)
last_page = int(html.cssselect('.last')[0].attrib['href'][-3:])
first_page = last_page - 10

urls = [url_fmt.format('?page=' + str(i)) for i in range(last_page, first_page, -1)]

def fetch(url):
  print(url)
  src =  requests.get(url).text
  html = lxml.html.fromstring(src)

  rows = html.xpath('//tr')
  rows.reverse()

  data = []

  for row in rows:
    tds = row.findall('td')
    if len(tds) == 0:
      continue

    tm = datetime.strptime(tds[1].text_content().strip(), time_fmt)
    tm = time.mktime(tm.timetuple())
    amount = float(tds[2].text_content().strip()[1:].replace(',', ''))
    data.append([tm, amount])
  return data

# let's not try and hit the tracker too hard during the marathon eh?
pool = ThreadPool(4)
for stuff in pool.imap(fetch, urls):
# for stuff in map(fetch, urls):
  data.extend(stuff)
#  time.sleep(2)

final = sorted(data, key=lambda x: x[0])

json.dump(final, open('scraped.json', 'w'))
