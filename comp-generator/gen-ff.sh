#!/bin/sh
python3 generate-json.py \
  --name "FF Comparison" \
  --glob "/home/alligator/dev/agdq-stats/frost*.json" \
  --glob "/home/alligator/dev/agdq-stats/flame*.json" \
  ff-comp.json
