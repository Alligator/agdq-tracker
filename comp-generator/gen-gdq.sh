#!/bin/sh
python3 generate-json.py \
  --name "GDQ Comparison" \
  --glob "/home/alligator/dev/agdq-stats/*gdq*.json" \
  comp.json

# ff
# cd /home/alligator/dev/agdq-tracker/agdq-tracker/comp-generator/
# python3 generate-json.py \
#   --glob "/home/alligator/dev/agdq-stats/frost*.json" \
#   --glob "/home/alligator/dev/agdq-stats/flame*.json" \
#   --glob "/home/alligator/dev/agdq-tracker/agdq-tracker/frost24/web/frost24.json" \
#   /var/www/gdq.alligatr.co.uk/ff-comparison/comp.json > /dev/null
