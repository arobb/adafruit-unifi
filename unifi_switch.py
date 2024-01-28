from enum import Enum
from typing import Optional

from pyunifi.controller import Controller

class Switch(object):
    """Class to manage Unifi Switches based on pyunifi.
    """
    MODE = Enum('Switch Mode', {'Auto': 'auto', 'Off': 'off', 'On': 'on'})

    def __init__(self, controller: Controller, device_mac: str):
        self.controller = controller
        self.config = controller.get_device_stat(device_mac)

    def get_port_overrides(self, key, value) -> dict:
        """Look up port by any port override parameter.

        port = get_port_overrides('port_idx', 5)
        {'autoneg': True,
          'egress_rate_limit_kbps_enabled': False,
          'excluded_networkconf_ids': [],
          'forward': 'customize',
          'isolation': False,
          'name': 'My Port Name',
          'native_networkconf_id': '6101e9....',
          'op_mode': 'switch',
          'poe_mode': 'auto',
          'port_idx': 2,
          'port_security_enabled': False,
          'port_security_mac_address': [],
          'setting_preference': 'manual',
          'show_traffic_restriction_as_allowlist': False}
        """
        port = None

        # Search for the port idx or port name in the list of ports
        for port_obj in self.config['port_overrides']:
            if port_obj[key] == value:
                port = port_obj
                break

        return port

    def _port_power(self, port_idx: int, mode: MODE) -> dict:
        """Internal function to do the dirty work of configuring port PoE power setting.

        Credit: https://github.com/finish06/pyunifi/blob/master/pyunifi/controller.py
        """
        device_id = self.config.get("_id")
        overrides = self.config.get("port_overrides")

        found = False
        if overrides:
            for i, port_override in enumerate(overrides):
                if overrides[i]["port_idx"] == port_idx:
                    # Override already exists, update..
                    overrides[i]["poe_mode"] = mode.value
                    found = True
                    break

        if not found:
            # Retrieve portconf
            portconf_id = None

            for port in self.config["port_table"]:
                if port["port_idx"] == port_idx:
                    portconf_id = port["portconf_id"]
                    break

            if portconf_id is None:
                raise Exception(f"Port ID %s not found in port_table{port_idx}")

            overrides.append(
                {
                    "port_idx": port_idx,
                    "portconf_id": portconf_id,
                    "poe_mode": mode.value
                }
            )

        # We return the device_id as it's needed by the parent method
        return {"port_overrides": overrides, "device_id": device_id}

    def port_power(self, port_idx: int, mode: MODE):
        params = self._port_power(port_idx, mode)
        device_id = params['device_id']
        del params['device_id']

        return self.controller._api_update("rest/device/" + device_id, params)

    def port_power_off(self, port_idx):
        return self.port_power(port_idx=port_idx, mode=self.MODE.Off)

    def port_power_on(self, port_idx):
        return self.port_power(port_idx=port_idx, mode=self.MODE.Auto)
