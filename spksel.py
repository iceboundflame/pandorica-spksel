#!/usr/bin/env python

from flask import Flask
import flask as fsk
import json

SWITCH_STATE_FILE = 'switches'
NUM_ROOMS = 5

app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.secret_key = 'dn389w3ka3ra8908v893jkd84njs9tm,s9vnwodf.bv90aw3v2300'

@app.route('/')
def index():
    title = 'spksel'

    return fsk.render_template('index.jade', title=title, switch_states=json.dumps(load_switch_states()))

@app.route('/switches', methods=['GET','POST'])
def switches():
    switch_states = load_switch_states()

    if fsk.request.method == 'POST' or fsk.request.values.get('room'):
        room = int(fsk.request.values.get('room'))
        val = fsk.request.values.get('val') == '1'
        assert room >= 0 and room < NUM_ROOMS

        print "Setting", room, val

        switch_states[room] = val
        # TODO: call control.py

        save_switch_states(switch_states)

    # show switch state
    return fsk.jsonify(switchStates=switch_states)


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


if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0')
    app.run(debug=True)
