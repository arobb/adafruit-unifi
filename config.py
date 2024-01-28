"""Configuration parser for Unifi and Adafruit.io

Basic structure based on https://github.com/adafruit/Pi_Physical_Dashboard/blob/master/config.py
"""

from configparser import SafeConfigParser

class SimpleObject(object):
    def __init__(self, **kwargs):
        if len(kwargs) == 0:
            pass

        for k, v in kwargs.items():
            setattr(self, k, v)


class Config(object):
    """Class to load credentials and configuration for the controller and IO integrations."""

    def __init__(self, filename):
        self._parser = SafeConfigParser()
        if len(self._parser.read(filename)) == 0:
            # Failed to load the config file, throw an error.
            raise RuntimeError('Failed to find configuration file with name: {0}'.format(filename))

        for section in self._parser.sections():
            params = dict(self._parser.items(section))
            setattr(self, section, SimpleObject(**params))