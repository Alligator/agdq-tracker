import json
import csv
import sys
import time
from dateutil import parser

MARATHON_NAME = 'gdqx23'

schedule = json.load(open(f'{MARATHON_NAME}_schedule.json'))
donations = json.load(open(f'{MARATHON_NAME}_donations.json'))
viewers_csv = list(csv.DictReader(open(f'{MARATHON_NAME}_viewers.csv')))

# tuples of (timestamp, viewers)
viewers = [(parser.parse(v['created_at']).timestamp(), v['viewer_count']) for v in viewers_csv]

# make sure everything is sorted
schedule = sorted(schedule, key=lambda x: x[0])
donations = sorted(donations, key=lambda x: x[0])
viewers = sorted(viewers, key=lambda x: x[0])

# take the start and end time from the schedule
start_time = schedule[0][0]
end_time = schedule[-1][0] + 3600

donation_index = 0
total_donations = 0

viewer_index = 0
last_viewer_value = 0

# every 60 seconds until the end
prev_time = 0
current_time = start_time
data = []
while current_time < end_time:
    # sum the donations between prev_time and current_time
    donations_in_bucket = 0
    while True:
        if donations[donation_index][0] > prev_time and donations[donation_index][0] <= current_time:
            donations_in_bucket += donations[donation_index][1]
            donation_index += 1
        else:
            break
    total_donations += donations_in_bucket

    # use viewer_index unless viewer_index + 1 is < current_time
    if viewer_index < len(viewers) - 1 and viewers[viewer_index+1][0] < current_time:
        viewer_index += 1

    current_viewers = int(viewers[viewer_index][1])
    # if the latest viewer thing is over 10 minutes away from current_time, use null instead
    if abs(viewers[viewer_index][0] - current_time) > 600:
        current_viewers = None

    data.append([current_time, current_viewers, total_donations])
    current_time += 60

stats = {
    'games': schedule,
    'viewers': data,
}

json.dump(stats, open(f'{MARATHON_NAME}_stats.json', 'w'), indent=2)
