import time
import inspect
import json
import os.path
from datetime import datetime

import requests
import lxml.html
from dateutil import parser

MARATHON_NAME = 'gdqx23'
TRACKER_URL = 'https://tracker.gamesdonequick.com/tracker/donations/GDQX2023'
SCHEDULE_ID = 45

def log(txt):
    print(datetime.now().isoformat(), f'[{inspect.stack()[1].function}]', txt)

def get_schedule():
  resp = requests.get(f'https://gamesdonequick.com/tracker/api/v2/events/{SCHEDULE_ID}/runs/')
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
    raise Exception('no games')
  return games

def get_donations():
    log('fetching page count')
    h = requests.get(TRACKER_URL).text
    html = lxml.html.fromstring(h)
    page_input = html.get_element_by_id('page')
    page_count = int(page_input.get('max'))
    log(f'{page_count} pages to fetch')

    data = []
    for i in range(1, page_count + 1):
        log(f'page {i}/{page_count}')
        params = { 'page': i }
        h = requests.get(TRACKER_URL, params=params).text
        html = lxml.html.fromstring(h)
        rows = html.xpath('//table/tr')
        for row in rows:
            tds = row.xpath('td')
            date_el = tds[1]
            amount_el = tds[2]

            date = parser.parse(date_el.text)
            amount = float(amount_el.text_content().replace('$', '').replace(',', '').strip())
            data.append((date.timestamp(), amount))
    return data

if not os.path.exists(f'{MARATHON_NAME}_schedule.json'):
    schedule = get_schedule()
    json.dump(schedule, open(f'{MARATHON_NAME}_schedule.json', 'w'), indent=2)

if not os.path.exists(f'{MARATHON_NAME}_donations.json'):
    donations = get_donations()
    json.dump(donations, open(f'{MARATHON_NAME}_donations.json', 'w'))
