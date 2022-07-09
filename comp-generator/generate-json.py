import re
import json
import math
from pprint import pprint
from glob import glob
from datetime import datetime

stats = {
    'ts': [],
    'marathons': [],
    'viewers': [],
    'donations': [],
}

def add_all_marathons():
    # the general idea
    # 1. read all the json files
    # 2. find the earliest timestamp, use it as the root
    # 3. generate 5 minute buckets for a week after the root
    # 4. offset each marathon to match the root
    # 5. truncate each ts to 5 minute accuracy
    # 6. store the largest no. of viewers and donations for each 5 min bucket

    marathon_files = glob('/home/alligator/dev/agdq-stats/*gdq*.json')
    def sort_key(f):
        m = re.search(r'([as])gdq(\d\d)', f)
        return m.group(2) + m.group(1)

    marathons = []
    marathon_names = []

    for file in sorted(marathon_files, key=sort_key, reverse=True):
        if 'sgdq14' in file:
            break
        marathon = json.load(open(file, 'r'))
        marathons.append(marathon)
        m = re.search(r'([as])gdq(\d\d)', file)
        marathon_names.append(m.group(0))

    # find the earliest start time
    earliest_start = min(m['viewers'][0][0] for m in marathons)

    # find 3pm on that day, that's the root timestamp
    root_ts = datetime.fromtimestamp(earliest_start) \
        .replace(hour=15, minute=0, second=0, microsecond=0) \
        .timestamp()

    # generate the timestamps
    # every 5 mins for 7 days
    timestamps = []
    for offset in range(0, 60 * 60 * 24 * 7, 5 * 60):
        timestamps.append(root_ts + offset)

    timestamp_map = { int(ts): i for i, ts in enumerate(timestamps) }

    # do the dang thing
    viewers = []
    donations = []
    meta = []

    for i, marathon in enumerate(marathons):
        print(datetime.now(), 'reading', marathon_names[i])
        viewers.append([None] * len(timestamps))
        donations.append([None] * len(timestamps))

        # find this marathon's 3pm start time and it's offset to the root ts
        start_time = marathon['viewers'][0][0]
        start_time_threepm = datetime.fromtimestamp(start_time) \
            .replace(hour=15, minute=0, second=0, microsecond=0) \
            .timestamp()
        seconds_to_offset = start_time_threepm - root_ts

        max_donations = 0
        max_viewers = 0
        max_viewers_ts = 0

        last_index = 0
        for v in marathon['viewers']:
            ts, v, d = v
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
                if d != None:
                    existing_donations = donations[-1][index]
                    donations[-1][index] = max(existing_donations if existing_donations != None else 0, d)
                    max_donations = max(d, max_donations)
                last_index = index

        # trim off the end
        viewers[-1] = viewers[-1][:last_index]

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
        'marathons': marathon_names,
        'ts': timestamps,
        'viewers': viewers,
        'donations': donations,
        'meta': meta,
    }

stats = add_all_marathons()
json.dump(stats, open('output.json', 'w'), indent=2)
