import aiohttp
import json

from .homeplusconst import SET_STATE_URL
from .homeplusmodule import HomePlusModule


class HomePlusInteractiveModule(HomePlusModule):
    """Base Class for Home+ modules that are interactive, i.e a Home+ device that accepts commands to update
    its status, such as a plug or a light

    This class extends the HomePlusModule base class.

    Attributes:
        status (str): The module can have status = 'on' or status = 'off'
        power (int): The module power consumption in watts (as an integer value)
    """

    STATUS_ON = True
    """ Data to be set in the API to set the device to an 'on' state."""

    STATUS_OFF = False
    """ Data to be set in the API to set the device to an 'off' state."""

    def __init__(self, plant, id, name, hw_type, device, bridge, fw="", type="", reachable=False):
        """HomePlusInteractiveModule Constructor

        Args:
            plant (HomePlusPlant): Plant that holds this module
            id (str): Unique identifier of the module
            name (str): Name of the module
            hw_type (str): Hardware/product of the module (NLP, NLT, NLF)
            device (str): Type of the device (plug, light, remote)
            bridge (str): Unique identifier of the bridge that controls this module
            fw (str, optional): Firmware revision of the module. Defaults to an empty string.
            type (str, optional): Additional type information of the module. Defaults to an empty string.
            reachable (bool, optional): True if the module is reachable and False if it is not. Defaults to False.
        """
        super().__init__(plant, id, name, hw_type, device, bridge, fw, type, reachable)
        self.status = ""
        self.power = 0

    def __str__(self):
        """Return the string representing this module"""
        return f"Home+ Interactive Module: device->{self.device}, name->{self.name}, id->{self.id}, reachable->{self.reachable}, status->{self.status}, bridge->{self.bridge}"

    def _build_state_data(self, desired_status):
        """Return the JSON structure that is to be sent in the POST request to update the module status"""
        state_param = {
            "home": {"id": self.plant.id, "modules": [{"id": self.id, "on": desired_status, "bridge": self.bridge}]}
        }
        return state_param

    def update_state(self, module_data):
        """Update the internal state of the module from the input JSON data.

        Args:
            module_data (json): JSON data of the module state
        """
        super().update_state(module_data)
        self.status = "on" if module_data.get("on") else "off"
        self.power = int(module_data.get("power", "0"))

    async def turn_on(self):
        """Turn on this interactive module"""
        if await self.post_status_update(HomePlusInteractiveModule.STATUS_ON):
            self.status = "on"

    async def turn_off(self):
        """Turn off this interactive module"""
        if await self.post_status_update(HomePlusInteractiveModule.STATUS_OFF):
            self.status = "off"

    async def toggle_status(self):
        """Toggle the state of this interactive module, i.e. if the module is on, the method call turns it off.
        If the module is off, the method call turns it on.
        """
        desired_status = HomePlusInteractiveModule.STATUS_OFF
        if self.status == "off":
            desired_status = HomePlusInteractiveModule.STATUS_ON

        if await self.post_status_update(desired_status):
            self.status = "on" if desired_status else "off"

    async def post_status_update(self, desired_end_status):
        """Call the API method to act on the module's status.

        Args:
            desired_end_status (boolean): One of the two class attributes (STATUS_ON and STATUS_OFF)
                                          that are defined to set the status ON or OFF.

        Returns:
            bool: True if the API update request was successful; False otherwise.
        """
        oauth_client = self.plant.oauth_client
        update_status_result = False
        try:
            await oauth_client.post_request(SET_STATE_URL, json=self._build_state_data(desired_end_status))
        except aiohttp.ClientResponseError:
            self.logger.error("HTTP client response error when posting module status")
        else:
            update_status_result = True
        return update_status_result
