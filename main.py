#!/usr/bin/env python3
import platform
import sys

# Import thrid party Unifi Python client
from pyunifi.controller import Controller

# Import Adafruit IO MQTT client
from Adafruit_IO import Client as AIO_Client
from Adafruit_IO import MQTTClient as AIO_MQTTClient
from Adafruit_IO import Data

from config import Config
from unifi_switch import Switch
from logger import Logger

# Load configuration and set log level
conf = Config('config.ini')
log = Logger()

def connected(client: AIO_MQTTClient):
    """Callback once Adafruit IO is connected

    Use to subscribe to feeds."""
    log.info('Connected to Adafruit IO')
    client.subscribe(conf.adafruit_io.feed)


def update_ports(client: AIO_MQTTClient, feed_id: str, payload: str):
    """Callback for updates from Adafruit IO"""
    # Check if this is the correct feed
    if feed_id != conf.adafruit_io.feed:
        log.error(f'Feed does not match. Given: {feed_id}, expecting: {conf.adafruit_io.feed}')
        return None

    # Configure whether the PoE mode is on (Auto) or off based on the payload.
    mode_setting = Switch.MODE.Off
    if int(payload) > 0:
        mode_setting = Switch.MODE.Auto

    # List of ports
    switch_ports_config = conf.switch_config()

    # Certificate chain
    cert_chain_file = conf.get_cert_chain_file()

    # Initialize the Unifi client
    log.info(f'Connecting to Unifi site {conf.unifi.site} at {conf.unifi.host}')
    unifi_client = Controller(host=conf.unifi.host,
                              port=conf.unifi.port,
                              username=conf.unifi.username,
                              password=conf.unifi.password,
                              site_id=conf.unifi.site,
                              ssl_verify=cert_chain_file)

    # Iterate through the port list
    for port in switch_ports_config:
        # Pull the switch and port configurations
        sw = Switch(unifi_client, port['mac'])
        port_config = sw.get_port_overrides('port_idx', int(port['idx']))

        # Skip configuring the port if it is already in the correct mode
        if port_config['poe_mode'] == mode_setting.value:
            log.warning('Port {0} on switch {1} already set to {2}'\
                .format(port['idx'], port['switch'], mode_setting.value))
            continue

        # Report the port information about to be updated
        log.warning('Setting PoE to {0} for port {1} (IDX: {2}) in switch {3}'\
            .format(mode_setting.value,
                    port_config['name'],
                    port['idx'],
                    port['switch']))

        # Send update
        sw.port_power(port_idx=port['idx'], mode=mode_setting)


def run():
    """Start the listener and wait on messages.

    BLOCKING"""
    log.warning("Starting Adafruit-Unifi Controller")

    # Report basic configuration
    log.debug(f'Unifi site: "{conf.unifi.site}"')
    log.debug(f'Adafruit feed: "{conf.adafruit_io.feed}"')

    # Configure Adafruit IO
    aio = AIO_Client(conf.adafruit_io.username, conf.adafruit_io.key)
    aio_mqtt = AIO_MQTTClient(conf.adafruit_io.username, conf.adafruit_io.key)

    # MQTT callback configuration
    aio_mqtt.on_connect = connected
    aio_mqtt.on_message = update_ports

    # Connect to Adafruit IO MQTT
    aio_mqtt.connect()

    # Get current value
    latest = aio.receive(feed=conf.adafruit_io.feed)  # Returns Adafruit_IO.Data object
    update_ports(aio_mqtt, conf.adafruit_io.feed, latest.value)

    # Run
    aio_mqtt.loop_blocking()


if __name__ == '__main__':
    run()
