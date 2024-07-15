Adafruit Unifi
==============
Runs a listener to an Adafruit IO feed to then turn PoE on and off for a list of Unifi switch ports.

Maintenance
-----------
1. Update Let's Encrypt certificate
2. Update list of current roots
   1. Look up the Unifi endpoint's certificate (through a browser)
   2. Check which CA's are in the signing chain
   3. Use https://letsencrypt.org/certificates/ to get current PEM URLs
   4. Update config.ini.template sections lets_encrypt_roots and lets_encrypt_ca
   5. Update use of the template file (Ansible or other means)

Run
---
`./main.py`: Starts a blocking process that listens to Adafruit IO and updates the ports. Ctrl-C to stop.

Daemon
------
`./adafruit-unifi-daemon.py`: Runs the listener/port update process as a daemon in the background. Stop with `kill -2 $(cat /tmp/adafruit-unifi.pid)`

Configure
---------
Copy `config_template.ini` to `config.ini` and update the values as appropriate.

Copy `switch_ports_template.yaml` to `switch_ports.yaml` and update the values as appropriate.