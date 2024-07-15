"""Configuration parser for Unifi and Adafruit.io

Basic structure based on https://github.com/adafruit/Pi_Physical_Dashboard/blob/master/config.py
"""
import os
import ssl
import yaml

from configparser import SafeConfigParser
from tempfile import NamedTemporaryFile
from urllib.request import urlopen


class SimpleObject(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __getattr__(self, item):
        return self.get(item)


class Config(object):
    """Class to load credentials and configuration for the controller and IO integrations."""

    def __init__(self, filename):
        self._parser = SafeConfigParser()
        self.cert_chain_file = None

        if not os.path.isfile(filename):
            filename = f'/etc/adafruit-unifi/{filename}'

        if len(self._parser.read(filename)) == 0:
            # Failed to load the config file, throw an error.
            raise RuntimeError('Failed to find configuration file with name: {0}'.format(filename))

        for section in self._parser.sections():
            params = dict(self._parser.items(section))
            setattr(self, section, SimpleObject(**params))

    def switch_config(self):
        """Load switch port configuration"""
        switch_ports_config_file = self.unifi.switch_ports_config

        if not os.path.isfile(switch_ports_config_file):
            switch_ports_config_file = f'/etc/adafruit-unifi/{switch_ports_config_file}'

        with open(switch_ports_config_file, 'r') as fh:
            switch_port_config = yaml.safe_load(fh)

        return switch_port_config['port_list']

    def _get_certificate_url_list(self):
        url_list = list()

        for ca, url in self.lets_encrypt_roots.items():
            url_list.append(url)

        for ca, url in self.lets_encrypt_ca.items():
            url_list.append(url)

        return url_list

    def get_cert_chain_file(self) -> str:
        """Download the certficate chain"""
        # Get the host's certificate
        host_cert = ssl.get_server_certificate((self.unifi.host, self.unifi.port))

        # Store the host and CA chain in a temp file
        if self.cert_chain_file is None:
            self.cert_chain_file = NamedTemporaryFile()
            self.cert_chain_file.write(host_cert.encode('UTF8'))

            # Download trusted CA certificates
            ca_url_list = self._get_certificate_url_list()
            for ca in ca_url_list:
                with urlopen(ca) as root_fh:
                    ca_cert = root_fh.read()
                    self.cert_chain_file.write(ca_cert)

            # Rewind the temp file so we start to read it from the beginning
            self.cert_chain_file.seek(0)

        return self.cert_chain_file.name
