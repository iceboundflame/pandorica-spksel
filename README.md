pandorica-spksel
================

Web interface for the multi-room audio controller

This is a Python 2.7/Flask application using jQuery Mobile.

control.py uses the RPi.GPIO Python module to pulse the GPIOs. Each execution will change the relay state to match. For instance:

    sudo ./control.py            # Turn off all relays
    sudo ./control.py 0 2 3      # Turn on relays 0, 2, and 3
    sudo ./control.py 0 1 2 3 4  # Turn on all relays

spksel.py is the actual Flask web server. It serves the web interface, calling "sudo ./control.py" in order to turn rooms on and off. It uses LIRC's "irsend" to send commands to the sound system via IR remote.

This is designed to be run in a virtualenv, so unpack virtualenv and run ./setup to install the necessary packages.


# Configuration notes

## Raspberry Pi pins used ##

    2   5V
    6   GND
    7   GPIO4
    11  GPIO17
    12  GPIO18
    13  GPIO27
    15  GPIO22
    16	GPIO23
    18  GPIO24
    22  GPIO25
    24  GPIO08
    26  GPIO07
    ?   GPIO9   IR receiver (not connected)
    23  GPIO11  IR emitter
    25  GND

To test the relay board, use control.py to make sure that all relays can click on and off. Adjust the PIN_MAP in control.py as necessary.


## spksel ##

Install nginx via apt and configure it to serve a uWSGI site on /.
Create spksel user, set up sudoers to allow "sudo control.py" without password.

Extract virtualenv, run ./setup in this repository to create "myenv" virtual environment and download Flask/Jinja2/other packages. Following deployment instructions at http://flaviusim.com/blog/Deploying-Flask-with-nginx-uWSGI-and-Supervisor/ :

    . myenv/bin/activate
    # After activating virtualenv:
    pip install uwsgi   # takes a while to build on RPi, ~15 min
    
    # Test:
    uwsgi -s /tmp/spksel.sock -w spksel:app -H /home/spksel/spksel/myenv --chmod-socket=666  --processes 4 --threads 2 --stats 127.0.0.1:9191

Set up supervisord to run uwsgi on bootup.


## LIRC ##

Install:

    sudo apt-get install lirc

Record remote with irrecord (using a USB receiver). I used the RC5 template (downloaded from the LIRC library) for my Philips MCM704D.

    irrecord -d /dev/lirc1 RC5

Rename the resulting RC5.conf to lircd.conf, edit the remote name to PhilipsHiFi. Move to `/etc/lirc/lircd.conf`

Install GPIO IR driver: [driver requires both in and out pin so we set an unused GPIO to be input]

    sudo modprobe lirc_rpi gpio_out_pin=11 gpio_in_pin=9

Test: The IR LED should blink and if in range of the receiver, turn it on/off.

    irsend SEND_ONCE PhilipsHiFi Power

Add to /etc/modules to load the lirc_rpi module at boot:

    lirc_rpi gpio_out_pin=11 gpio_in_pin=9


## ShairPort ##

AirPlay support is handled entirely by the ShairPort package. Just switch the sound input to Aux and connect the aux cable to the Raspberry Pi. The audio quality is sufficient for my purposes, but for better audio, you might consider adding a USB soundcard to the Pi.

Install perl-net-sdp:

    git clone https://github.com/njh/perl-net-sdp.git perl-net-sdp
    cd perl-net-sdp
    perl Build.PL
    sudo ./Build
    sudo ./Build test
    sudo ./Build install
    cd ..

Install shairport:

    git clone https://github.com/hendrikw82/shairport.git
    cd shairport
    make
    make install
    cp shairport.init.sample /etc/init.d/shairport
    cd /etc/init.d
    chmod a+x shairport
    update-rc.d shairport defaults

Edit /etc/init.d/shairport to change the AirPlay server name:

    DAEMON_ARGS="-w $PIDFILE -a Pandorica"

For some reason, streaming wouldn't work for me until I enabled ipv6. Add "ipv6" as the last line to /etc/modules.
