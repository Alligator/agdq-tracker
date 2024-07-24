#!/bin/sh
python3 generate-json.py \
  --name "GDQx Comparison" \
  --glob "/home/alligator/dev/agdq-stats/gdqx*.json" \
  gdqx-comp.json
