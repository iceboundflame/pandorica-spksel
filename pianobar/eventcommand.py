#!/usr/bin/env python

"""Simple eventcommand script for pianobar which writes all available information to a
JSON file. Example:

{
    "album": "I'm Not The Only One (Single)",
    "artist": "Sam Smith",
    "coverArt": "http://cont-sjl-1.pandora.com/images/public/amz/2/8/6/8/800048682_500W_500H.jpg",
    "pRet": "1",
    "pRetStr": "Everything is fine :)",
    "rating": "0",
    "songDuration": "239",
    "songPlayed": "0",
    "songStationName": "",
    "stationCount": "77",
    "stationName": "Today's Hits Radio",
    "stations": {
        "0": "(+44) Radio",
        "1": "12:51 Radio",
        ...
    },
    "title": "I'm Not The Only One",
    "wRet": "1",
    "wRetStr": "Everything's fine :)"
}
"""

import json
import os
import re
import sys

STATUS_FILE = os.path.join(os.environ['HOME'], '.config/pianobar/status')

command = sys.argv[1]
print command
# if True:
if command in ('songstart', 'songlove', 'songban', 'usergetstations', 'stationcreate',
               'stationaddgenre', 'songexplain', 'stationaddshared', 'stationdelete'):
    status = {}
    stations = {}
    for line in sys.stdin:
        try:
            key, value = line.strip().split('=', 2)

            m = re.match('station(\d+)', key)
            if m:
                stations[int(m.group(1))] = value
            else:
                status[key] = value
        except ValueError:
            pass

        status['stations'] = stations

        with open(STATUS_FILE, 'w') as fh:
            fh.write(json.dumps(status))