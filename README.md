# agdq-tracker
The various bits and pieces that make up my [*gdq tracker](https://irc.alligatr.co.uk/sgdq19/).
This is a cobbled together bunch of scripts and other bits and pieces and I
don't intend anyone except me to run it.

## setting up a new marathon
Copy config.example.sh to config.sh and fill in the everything, except the
twitch variables, which are covered next.

### twitch stuff
Get twitch client id and secret from https://dev.twitch.tv/console/apps, put
them in config.sh.

Run `twitch-utils/get-access-token.sh`, this will use the client id and secret
to get an access token. Copy it into config.sh.

Run `twitch-utils/test-access-token.sh`, passing in the username of a live
twitch streamer. This will call a couple of endpoints and should print some
info about the stream. If it doesn't the token probably doesn't work.

## how it works

### the cron job
This is run by cron every minute. It fetches the viewer count from the twitch
API, the donation total from the tracker API and scrapes the schedule from the
schedule page.

This script isn't pretty but it's been proven to not die very often over the
years. It attempts to recover from any errors and write a null in place of the
data it would have written, to ensure there's a record in the JSON for every
minute no matter what.

The cron job looks something like this:

    * * * * *  cd /home/alligator/dev/agdq-tracker/sgdq19 && /home/alligator/.local/bin/pipenv run python get-data.py

### the web interface
This is the code for the actual tracker you see. As before the code is real
ugly (and *ancient* in terms of JS coding standards) but it continues to work
with only minor tweaks, so it's here to stay I guess.

----

## other stuff

`misc/comparison` contains the code for the [comparison chart](https://irc.alligatr.co.uk/agdq-comparison/).
This was hacked together quickly and it shows. I've fixed it up a couple of
times over the years to make it less dog slow but it's still very rough. It
took about 30 minutes to smash together and tends to be more popular than the
main tracker come marathon time, so there you go.

`misc/original-tracker` contains the code for the [original tracker](https://irc.alligatr.co.uk/sgdq)
, which used the google charts API instead of d3.

`misc/gdq-announce.py` a very simple python script that looks at the json
output from the tracker and posts a message to a discord webhook when a new
game is coming up. i point it at a gdq specific channel on a discord server so
people can always see what's on now and what's up next.
