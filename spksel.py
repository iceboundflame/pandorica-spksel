#!/usr/bin/env python

# Webapp server for speaker selector/audio control
#
# Copyright (C) 2013 David Liu (http://iceboundflame.com)
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
from flask import Flask
import flask as fsk
import json
import subprocess
import re
import sys
import pickle


VALID_SOURCES = ['Cd', 'Tuner', 'Aux']
NUM_ROOMS = 5
STATE_FILE = './state.dat'
DEFAULT_STATE = dict(switches=[False]*NUM_ROOMS, source='Cd')

ENABLE_EXEC = True
SWITCH_EXEC = ['sudo', './control.py']
IR_EXEC = ['irsend', 'SEND_ONCE', 'PhilipsHiFi']

app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')


@app.route('/')
def index():
    return fsk.render_template('index.jade', state=json.dumps(load_state()))

@app.route('/state')
def state():
    state = load_state()
    return fsk.jsonify(state)

@app.route('/switches', methods=['GET','POST'])
def switches():
    room = int(fsk.request.values.get('room'))
    val = fsk.request.values.get('val') == '1'
    assert room >= 0 and room < NUM_ROOMS

    print("Setting switch", room, val)
    state = load_state()
    state['switches'][room] = val
    save_state(state)
    set_switches(state['switches'])

    return fsk.jsonify(state)

@app.route('/ir', methods=['GET','POST'])
def ir():
    ir = fsk.request.values.get('ir')
    assert re.match(r'^[A-Za-z0-9 ]+$', ir)

    if ENABLE_EXEC:
        try:
            subprocess.check_output(IR_EXEC + ir.split(),
                    stderr=subprocess.STDOUT)
        except Exception as e:
            print("Error calling irsend:\n", e, file=sys.stderr)
    else:
        print(IR_EXEC + ir.split())

    state = load_state()
    if ir in VALID_SOURCES:
        print("Saving source selection")
        state['source'] = ir
        save_state(state)

    return fsk.jsonify(state)


# Not really concurrency safe, but only one or two users will ever really use
# this at a time.
def load_state():
    state = DEFAULT_STATE
    try:
        with open(STATE_FILE, 'r') as f:
            state = pickle.load(f)

        assert len(state['switches']) == NUM_ROOMS
        assert state['source'] in VALID_SOURCES
    except Exception as e:
        print("Error loading persisted state", file=sys.stderr)
        state = DEFAULT_STATE

    return state

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        pickle.dump(state, f)

def set_switches(switches):
    on_rooms = filter(lambda x: switches[x], range(len(switches)))
    if ENABLE_EXEC:
        try:
            subprocess.check_output(SWITCH_EXEC + map(str, on_rooms),
                    stderr=subprocess.STDOUT)
        except Exception as e:
            print("Error calling switch control script:\n", e, file=sys.stderr)
    else:
        print(SWITCH_EXEC + map(str, on_rooms))



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
