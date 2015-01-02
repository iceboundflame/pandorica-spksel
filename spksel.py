#!/usr/bin/env python

# Webapp server for speaker selector/audio control
#
# Copyright (C) 2013-2014 David Liu (http://iceboundflame.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import flask
import json
import subprocess
import re
import sys
import time
from pianobar_control import PianoBar


SOURCES = {'Cd': 'PhilipsHiFi Cd',
           'Tuner': 'PhilipsHiFi Tuner',
           'Usb': 'PhilipsHiFiUsb Usb',
           'AirPlay': 'PhilipsHiFi Aux',
           'Pandora': 'PhilipsHiFi Aux',
           'Ipod': 'PhilipsHiFi Ipod'}
NUM_ROOMS = 5
STATE_FILE = './state.dat'
DEFAULT_STATE = dict(switches=[False]*NUM_ROOMS, source='Cd')

ENABLE_EXEC = True
SWITCH_EXEC = ['sudo', './control.py']
IR_EXEC = ['irsend', 'SEND_ONCE']

app = flask.Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

pianobar = None


def do_exec(command):
    print("Exec:", command)
    if ENABLE_EXEC:
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT)
        except Exception as e:
            print("Error calling", command, ":\n", e, file=sys.stderr)


@app.route('/')
def index():
    state = load_state()
    add_pandora_status(state)
    return flask.render_template('index.jade', state=json.dumps(state))


@app.route('/state')
def state():
    state = load_state()
    add_pandora_status(state)
    return flask.jsonify(state)


@app.route('/switches', methods=['GET','POST'])
def switches():
    room = int(flask.request.values.get('room'))
    val = flask.request.values.get('val') == '1'
    assert 0 <= room < NUM_ROOMS

    print("Setting switch", room, val)
    state = load_state()
    state['switches'][room] = val
    save_state(state)
    set_switches(state['switches'])

    add_pandora_status(state)
    return flask.jsonify(state)


@app.route('/ir', methods=['GET','POST'])
def ir():
    ir = flask.request.values.get('ir')
    assert re.match(r'^[A-Za-z0-9 ]+$', ir)

    do_exec(IR_EXEC + ir.split())
    state = load_state()

    add_pandora_status(state)
    return flask.jsonify(state)


@app.route('/source', methods=['GET','POST'])
def source():
    source = flask.request.values.get('source')
    assert source in SOURCES

    do_exec(IR_EXEC + SOURCES[source].split())

    global pianobar
    if source == 'Pandora':
        if pianobar and pianobar.is_running():
            pianobar.play()
        else:
            restart_pianobar()
    else:
        if pianobar and pianobar.is_running():
            pianobar.pause()

    state = load_state()
    state['source'] = source
    save_state(state)

    add_pandora_status(state)
    return flask.jsonify(state)


@app.route('/pandora', methods=['GET','POST'])
def pandora():
    cmd = flask.request.values.get('cmd')
    if cmd:
        if cmd in {'play', 'pause', 'skip', 'love', 'ban', 'tired'}:
            getattr(pianobar, cmd)()
        elif cmd in {'select_station'}:
            getattr(pianobar, cmd)(flask.request.values.get('arg'))
            time.sleep(1)  # allow status file to be updated.
        elif cmd == 'restart':
            restart_pianobar()
        else:
            raise ValueError("Unknown command")

    state = load_state()
    add_pandora_status(state)
    return flask.jsonify(state)


# Not really concurrency safe, but only one or two users will ever really use
# this at a time.
def load_state():
    state = DEFAULT_STATE
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)

        assert len(state['switches']) == NUM_ROOMS
        assert state['source'] in SOURCES
    except Exception as e:
        print("Error loading persisted state", file=sys.stderr)
        state = DEFAULT_STATE

    return state


def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)


def set_switches(switches):
    on_rooms = filter(lambda x: switches[x], range(len(switches)))
    do_exec(SWITCH_EXEC + map(str, on_rooms))


def add_pandora_status(state):
    global pianobar
    if pianobar and pianobar.is_running():
        state['pandora'] = pianobar.status()


def restart_pianobar():
    global pianobar
    if pianobar and pianobar.is_running():
        pianobar.quit()
    pianobar = PianoBar()
    pianobar.run()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--no_exec', help='disable execution of control commands (for testing)', action='store_true')
    parser.add_argument('--bind', help='IP to listen on', default='127.0.0.1')
    parser.add_argument('--port', help='port to listen on', default=5000)
    parser.add_argument('--debug', help='debug mode', default=True)
    args = parser.parse_args()

    ENABLE_EXEC = not args.no_exec

    app.run(debug=args.debug, host=args.bind, port=args.port)
