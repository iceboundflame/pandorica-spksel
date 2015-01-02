import json
import re
import subprocess
import os
from threading import Timer

PIANOBAR_BIN = '/opt/pianobar/bin/pianobar'

PIANOBAR_FOLDER = os.path.join(os.environ['HOME'], '.config/pianobar')
PIANOBAR_CTL = os.path.join(PIANOBAR_FOLDER, 'ctl')
PIANOBAR_STATUS = os.path.join(PIANOBAR_FOLDER, 'status')


def is_pianobar_running():
    return subprocess.call(['pidof', 'pianobar']) == 0


def kill_other_pianobars():
    subprocess.call(['killall', '-9', 'pianobar'])


class PianoBar(object):
    def __init__(self):
        self.proc = None
        self.devnull = open('/dev/null', 'w')
        # self.mode = STATION_SELECT
        self._is_paused = True

    def run(self):
        if is_pianobar_running():
            kill_other_pianobars()

        os.remove(PIANOBAR_STATUS)

        self.proc = subprocess.Popen(PIANOBAR_BIN,
                                     stdin=subprocess.PIPE,
                                     stdout=self.devnull,
                                     stderr=subprocess.STDOUT,
                                     close_fds=True)

        # select no station to start
        self._write_pianobar('')

    def quit(self):
        if self.proc:
            QUIT_TIMEOUT = 1  # seconds

            # Try to quit gracefully to allow pianobar to save its state file
            self._write_pianobar('q')

            # Timeout and force kill if necessary
            timer = Timer(QUIT_TIMEOUT, lambda: self.proc.kill())
            timer.start()
            self.proc.wait()
            timer.cancel()

            self.proc = None
        # kill_other_pianobars()

    def is_running(self):
        return self.proc is not None

    def status(self):
        try:
            with open(PIANOBAR_STATUS, 'r') as fh:
                status = json.load(fh)
                status.update({'paused': self._is_paused})
                return status
        except IOError:
            return None

    def select_station(self, station_id):
        assert re.match(r'\d+', station_id)
        self._write_pianobar('s' + station_id)

    def play(self):
        self._write_pianobar('P')
        status = self.status()
        if status and status.get('stationName'):
            self._is_paused = False

    def pause(self):
        self._write_pianobar('S')
        self._is_paused = True

    def skip(self):
        self._write_pianobar('n')

    def love(self):
        self._write_pianobar('+')

    def ban(self):
        self._write_pianobar('-')

    def tired(self):
        self._write_pianobar('t')

    def _write_pianobar(self, command):
        if self.proc:
            self.proc.stdin.write(command + '\n')
            print("Pianobar>>:", command + '\n')
        else:
            print("Pianobar NOT RUNNING>>:", command + '\n')
