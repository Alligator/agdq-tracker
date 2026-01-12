import re
import json
import math
import sys
import os
import argparse
from pprint import pprint
from glob import glob
from datetime import datetime

stats = {
    'ts': [],
    'marathons': [],
    'viewers': [],
    'donations': [],
}

parser = argparse.ArgumentParser()
parser.add_argument('--name', required=True)
parser.add_argument('--glob', required=True, action='append')
parser.add_argument('output_file', type=argparse.FileType('w'))
args = parser.parse_args()

def add_all_marathons(globs):
    # the general idea
    # 1. read all the json files
    # 2. find the earliest timestamp, use it as the root
    # 3. generate 5 minute buckets for a week after the root
    # 4. offset each marathon to match the root
    # 5. truncate each ts to 5 minute accuracy
    # 6. store the largest no. of viewers and donations for each 5 min bucket

    marathon_files = []
    for pat in globs:
        marathon_files += glob(pat)

    order = ['agdq', 'frost', 'sgdq', 'flame', 'gdqx']
    def sort_key(f):
        m = re.search(r'([a-z]+)(\d\d)', f)
        order_idx = order.index(m.group(1))
        return m.group(2) + str(order_idx)

    marathons = []
    marathon_names = []

    for file in sorted(marathon_files, key=sort_key, reverse=True):
        if 'sgdq14' in file:
            break
        marathon = json.load(open(file, 'r'))
        if 'sgdq17' in file:
            # sgdq17 hack
            # this has an extra day's worth of data at the start
            # chop it off
            marathon['viewers'] = marathon['viewers'][1200:]
        marathons.append(marathon)
        marathon_names.append(os.path.basename(file).split('.')[0])

    # find the earliest start time
    earliest_start = min(m['viewers'][0][0] for m in marathons if len(m['viewers']) > 0)

    # find 3pm on that day, that's the root timestamp
    root_ts = datetime.fromtimestamp(earliest_start) \
        .replace(hour=15, minute=0, second=0, microsecond=0) \
        .timestamp()

    # generate the timestamps
    # every 5 mins for 7 days
    timestamps = []
    days = 3 if 'gdqx' in file else 7
    for offset in range(0, 60 * 60 * 24 * days, 5 * 60):
        timestamps.append(root_ts + offset)

    timestamp_map = { int(ts): i for i, ts in enumerate(timestamps) }

    # do the dang thing
    viewers = []
    viewers_yt = []
    donations = []
    meta = []

    for i, marathon in enumerate(marathons):
        print(datetime.now(), 'reading', marathon_names[i])
        if len(marathon['viewers']) == 0:
            viewers.append([])
            viewers_yt.append([])
            donations.append([])
            continue
        viewers.append([None] * len(timestamps))
        viewers_yt.append([None] * len(timestamps))
        donations.append([None] * len(timestamps))

        # find this marathon's 3pm start time and it's offset to the root ts
        # start_time = marathon['viewers'][0][0]
        start_time = marathon['games'][0][0]
        start_time_threepm = datetime.fromtimestamp(start_time) \
            .replace(hour=15, minute=0, second=0, microsecond=0) \
            .timestamp()
        seconds_to_offset = start_time_threepm - root_ts

        max_donations = 0
        max_viewers = 0
        max_viewers_ts = 0

        last_index = 0
        for vv in marathon['viewers']:
            ts = vv[0]
            v = vv[1]
            d = vv[2]
            # truncate ts to 5 minutes
            truncated_ts = math.floor(ts / (5 * 60)) * (5 * 60)
            offset_ts = int(truncated_ts - seconds_to_offset)

            if offset_ts in timestamp_map:
                index = timestamp_map[offset_ts]
                if v != None:
                    existing_viewers = viewers[-1][index]
                    viewers[-1][index] = max(existing_viewers if existing_viewers != None else 0, v)
                    if v > max_viewers:
                        max_viewers = v
                        max_viewers_ts = int(ts)

                if len(vv) == 4 and vv[3] != None:
                    yt_v = vv[3]
                    existing_viewers = viewers_yt[-1][index]
                    viewers_yt[-1][index] = max(existing_viewers if existing_viewers != None else 0, yt_v)

                if d != None:
                    existing_donations = donations[-1][index]
                    donations[-1][index] = max(existing_donations if existing_donations != None else 0, d)
                    max_donations = max(d, max_donations)
                last_index = index

        # trim off the end
        viewers[-1] = viewers[-1][:last_index]
        viewers_yt[-1] = viewers_yt[-1][:last_index]

        # extend the last donation count until the end
        for i in range(last_index, len(donations[-1])):
            donations[-1][i] = max_donations

        # find the game at peak viewers
        max_viewers_game = None
        for game in marathon['games']:
            ts, name = game[:2]
            if ts < max_viewers_ts:
                max_viewers_game = name

        meta.append({
            'max_donations': max_donations,
            'max_viewers': max_viewers,
            'max_viewers_ts': max_viewers_ts,
            'max_viewers_game': max_viewers_game,
        })

    return {
        'name': args.name,
        'marathons': marathon_names,
        'ts': timestamps,
        'viewers': viewers,
        'viewers_yt': viewers_yt,
        'donations': donations,
        'meta': meta,
    }

stats = add_all_marathons(args.glob)
json.dump(stats, args.output_file)
