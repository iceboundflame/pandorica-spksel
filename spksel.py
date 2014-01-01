#!/usr/bin/env python

from flask import Flask
import flask as fsk
import json
import subprocess
import re

SWITCH_STATE_FILE = './switches'
NUM_ROOMS = 5

SWITCH_CONTROLLER = ['sudo', './control.py']

REMOTE = 'PhilipsHiFi'

app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.secret_key = 'dn389w3ka3ra8908v893jkd84njs9tm,s9vnwodf.bv90aw3v2300'

@app.route('/')
def index():
    return fsk.render_template('index.jade', switch_states=json.dumps(load_switch_states()))

@app.route('/switches', methods=['GET','POST'])
def switches():
    switch_states = load_switch_states()

    if fsk.request.method == 'POST' or fsk.request.values.get('room'):
        room = int(fsk.request.values.get('room'))
        val = fsk.request.values.get('val') == '1'
        assert room >= 0 and room < NUM_ROOMS

        print "Setting", room, val
        switch_states[room] = val
        set_switch_states(switch_states)
        save_switch_states(switch_states)

    # show switch state
    return fsk.jsonify(ok=True, switchStates=switch_states)

@app.route('/ir', methods=['GET','POST'])
def ir():
    ir = fsk.request.values.get('ir')
    assert re.match(r'^[A-Za-z0-9]+$', ir)

    try:
        subprocess.check_output(['irsend', 'SEND_ONCE', REMOTE, ir],
                stderr=subprocess.STDOUT)
    except (OSError, subprocess.CalledProcessError) as e:
        print "Error calling irsend:\n", e

    return fsk.jsonify(ok=True)

def load_switch_states():
    switch_states = None
    try:
        with open(SWITCH_STATE_FILE, 'r') as f:
            switch_states = map(lambda x: x == 'True', f.read().split())
    except:
        pass
    if not switch_states or len(switch_states) != NUM_ROOMS:
        switch_states = [False] * NUM_ROOMS

    return switch_states

def save_switch_states(switch_states):
    with open(SWITCH_STATE_FILE, 'w') as f:
        f.write(' '.join(map(str, switch_states)))

def set_switch_states(switch_states):
    on_rooms = filter(lambda x: switch_states[x], range(len(switch_states)))
    try:
        subprocess.check_output(SWITCH_CONTROLLER + map(str, on_rooms),
                stderr=subprocess.STDOUT)
    except (OSError, subprocess.CalledProcessError) as e:
        print "Error calling switch control script:\n", e



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    # app.run(debug=True)
