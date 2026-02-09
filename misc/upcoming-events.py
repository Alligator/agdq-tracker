import argparse
import requests
from datetime import datetime, timedelta, timezone
from dateutil import parser

arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--user-id', required=True)
arg_parser.add_argument('--webhook', required=True)
args = arg_parser.parse_args()

resp = requests.get('https://tracker.gamesdonequick.com/tracker/api/v2/events/')
resp.raise_for_status()
events = resp.json()

now = datetime.now(timezone.utc)
oneweek = now + timedelta(days=14)
msg = ''

for evt in events['results']:
    d = parser.parse(evt['datetime'])
    if d.timestamp() < now.timestamp():
        continue
    if d.timestamp() < oneweek.timestamp():
        delta = d - now
        msg += f'- {evt["name"]} starts in {delta.days} days\n'

if len(msg) > 0:
    content = f'<@{args.user_id}> there are upcoming GDQ events\n{msg}'
    requests.post(args.webhook, json={ 'content': content })
