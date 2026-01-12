# this file is for taking a partially completed marathon and reconstructing donations
# from the scraper
import json
import sys

MARATHON_FILE = 'agdq26.json'
DONATIONS_FILE = 'agdq26_donations.json'

marathon = json.load(open(MARATHON_FILE))
donations = json.load(open(DONATIONS_FILE))

schedule = marathon['games']

# make sure everything is sorted
schedule = sorted(schedule, key=lambda x: x[0])
donations = sorted(donations, key=lambda x: x[0])

# take the start and end time from the schedule
start_time = schedule[0][0]
end_time = schedule[-1][0] + 3600

new_viewers = []
donation_index = 0
total_donations = 0
ts = 0

# 1. loop over viewers, total up donations for time bucket, store
for v in marathon['viewers']:
    ts = v[0]

    # sum the donations in this tine bucket
    donations_in_bucket = 0
    while True:
        d = donations[donation_index]
        if d[0] > ts:
            break
        else:
            donations_in_bucket += d[1]
            donation_index += 1
    total_donations += donations_in_bucket

    # add it to new_viwers, copying over the rest of the array
    nv = v[:]
    nv[2] = total_donations
    new_viewers.append(nv)

# 2. contiue from where we stopped, total up donations and step 1 min
ts += 60
while ts < end_time:
    donations_in_bucket = 0
    while True:
        d = donations[donation_index]
        if d[0] > ts:
            break
        else:
            donations_in_bucket += d[1]
            donation_index += 1
    total_donations += donations_in_bucket
    print('adding new record at', ts)
    new_viewers.append([ts, None, total_donations])
    ts += 60

new_file = MARATHON_FILE.split('.')[0] + '_new.json'
print(f'writing to {new_file}')
marathon['viewers'] = new_viewers
json.dump(marathon, open(new_file, 'w'))
