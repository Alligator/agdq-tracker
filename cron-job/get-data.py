import json
import time
import sys
import requests
import re
import configparser
import argparse
import os.path

import lxml.html
from datetime import datetime, timedelta
from dateutil import parser

from pprint import pprint

arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--name', required=True)
arg_parser.add_argument('--type', required=True, choices=['gdq', 'gdqx', 'ff', 'btb', 'gdqueer'])
arg_parser.add_argument(
    '--start-date',
    required=True,
    type=parser.parse)
arg_parser.add_argument(
    '--end-date',
    required=True,
    type=parser.parse)
arg_parser.add_argument(
    '--force',
    action='store_true')
arg_parser.add_argument('--twitch-client-id', required=True)
arg_parser.add_argument('--twitch-access-token', required=True)
arg_parser.add_argument('--tracker-marathon-name', required=True)
arg_parser.add_argument('--tracker-marathon-id', required=True)
arg_parser.add_argument('--yt-api-key', required=True)
arg_parser.add_argument('output_file')

args = arg_parser.parse_args()

current_time = time.time()
start_date = args.start_date
end_date = args.end_date
now = datetime.utcnow().timestamp()
if not args.force and (now < start_date.timestamp() or now > end_date.timestamp()):
  sys.exit(0)


try:
  current_stats = json.load(open(args.output_file))
except IOError as e:
  current_stats = {
    'marathon_name': args.name,
    'marathon_type': args.type,
    'viewers': [],
    'games': [],
  }

# get viewers
for i in range(3):
  try:
    headers = {
      'Client-ID': args.twitch_client_id,
      'Authorization': f'Bearer {args.twitch_access_token}',
    }
    resp = requests.get('https://api.twitch.tv/helix/streams?user_id=22510310', headers=headers, verify=True, timeout=10.0)
    resp.raise_for_status()
    j = resp.json()
    if len(j['data']) == 0:
        t = None
        break;
    t = j['data'][0]['viewer_count']
    break
  except Exception as e:
    # write out a null
    sys.stderr.write('viewers ' + repr(e) + '\n')
    t = None

# get yt viewers
def get_yt_viewers(video_id):
    params = {
        'id': video_id,
        'key': args.yt_api_key,
        'part': 'liveStreamingDetails',
    }
    resp = requests.get('https://www.googleapis.com/youtube/v3/videos', params=params)
    j = resp.json()

    items = j.get('items', [])
    if not items:
        return None
    return items[0]['liveStreamingDetails']

def get_yt_video_id(channel_id):
    # at most every 15 mins
    now = datetime.utcnow()
    if now.minute % 15 != 0:
        return None

    params = {
        'part': 'id',
        'channelId': channel_id,
        'eventType': 'live',
        'type': 'video',
        'maxResults': '1',
        'key': args.yt_api_key,
        'fields': 'items/id/videoId',
    }
    resp = requests.get('https://www.googleapis.com/youtube/v3/search', params=params)
    resp.raise_for_status()
    j = resp.json()

    items = j.get('items', [])
    if not items:
        return None
    return items[0]['id']['videoId']

def get_cached_yt_video_id():
    if os.path.exists('/tmp/gdq-yt-id'):
        id = open('/tmp/gdq-yt-id').read()
        if len(id) == 0:
            return None
        return id
    return None

def set_cached_yt_video_id(video_id):
    with open('/tmp/gdq-yt-id', 'w') as f:
        if video_id is not None:
            f.write(video_id)

# yt_viewers = None
try:
    video_id = get_cached_yt_video_id()

    # no cached video id, try to get a new one
    if video_id is None:
        video_id = get_yt_video_id('UCI3DTtB-a3fJPjKtQ5kYHfA')
        set_cached_yt_video_id(video_id)

    # still no video id, not live
    if video_id is None:
        yt_viewers = None
    else:
        stream = get_yt_viewers(video_id)
        if stream is not None and 'concurrentViewers' in stream:
            yt_viewers = int(stream['concurrentViewers'])
        else:
            yt_viewers = None
            # clear the cache so we re-fetch next time
            set_cached_yt_video_id('')
except Exception as e:
    sys.stderr.write('yt viewers ' + repr(e) + '\n')
    yt_viewers = None

# get donations
try:
  j = json.loads(requests.get(f'https://tracker.gamesdonequick.com/tracker/api/v2/events/{args.tracker_marathon_id}/?totals').text)
  dn = float(j['donation_total'])
except Exception as e:
  sys.stderr.write('donations ' + repr(e) + '\n')
  dn = None

current_stats['viewers'].append((current_time, t, dn, yt_viewers))

# get schedule
try:
  resp = requests.get(f'https://tracker.gamesdonequick.com/tracker/api/v2/events/{args.tracker_marathon_id}/runs/')
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
  sys.stderr.write('games ' + repr(e) + '\n')
  pass

json.dump(current_stats, open(args.output_file, 'w'))
