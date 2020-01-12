import json
import sys
from pprint import pprint

scraped = json.load(open('scraped.json', 'r'))
tracked = json.load(open('agdq20.json', 'r'))

old_viewers = tracked['viewers']
new_viewers = tracked['viewers'].copy()

gap_start = 1578354610
gap_end = 1578382384
total = 0.0
current_time = None
prev_time = None

i = 0;
for (i, item) in enumerate(old_viewers):
    [time, viewers, donations] = item

    if time > gap_end:
        break

    if time < gap_start:
        if donations is not None:
            total = max(total, donations)
        prev_time = current_time
        current_time = time
        continue

    # we in it now
    # total up all the donations that were between now and prev
    # print(f'in gap {time} {viewers} {donations}')
    # print(f'current: {current_time} prev: {prev_time}')
    # print(f'total: {total}')
    donations = filter(lambda x: x[0] > prev_time and x[0] <= current_time, scraped);
    added = sum(x[1] for x in donations)
    total += added

    new_viewers[i] = [time, viewers, total]

    prev_time = current_time
    current_time = time

tracked['viewers'] = new_viewers
json.dump(tracked, open('agdq20-scraped.json', 'w'))
