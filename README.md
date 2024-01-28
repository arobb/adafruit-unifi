Adafruit Unifi
==============
Runs a listener to an Adafruit IO feed to then turn PoE on and off for a list of Unifi switch ports.

Run
---
`./main.py`: Starts a blocking process that listens to Adafruit IO and updates the ports. Ctrl-C to stop.

Daemon
------
`./adafruit-unifi-daemon.py`: Runs the listener/port update process as a daemon in the background. Stop with `kill -2 $(cat /tmp/adafruit-unifi.pid)`

Configure
---------
Copy `config_template.ini` to `config.ini` and update the values as appropriate.