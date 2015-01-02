import json
import subprocess
import os

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
        # self.mode = STATION_SELECT

    def start(self):
        if is_pianobar_running():
            kill_other_pianobars()

        os.remove(PIANOBAR_STATUS)

        self.devnull = open('/dev/null', 'w')
        self.proc = subprocess.Popen(PIANOBAR_BIN,
                                     stdin=subprocess.PIPE,
                                     stdout=self.devnull,
                                     stderr=subprocess.STDOUT)

        # select no station to start
        self._write_pianobar('')

    def status(self):
        try:
            with open(PIANOBAR_STATUS, 'r') as fh:
                return json.load(fh)
        except IOError:
            return None

    def stop(self):
        self.proc.terminate()

    def select_station(self):
        self.proc.terminate()

    def play(self):
        self._write_pianobar('P')

    def pause(self):
        self._write_pianobar('S')

    def like(self):
        self._write_pianobar('+')

    def ban(self):
        self._write_pianobar('-')

    def tired(self):
        self._write_pianobar('t')

    def tired(self):
        self._write_pianobar('t')

    def _write_pianobar(self, command):
        if self.proc:
            self.proc.stdin.write(command + '\n')
