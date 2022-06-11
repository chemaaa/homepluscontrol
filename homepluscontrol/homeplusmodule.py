import json
import logging

import aiohttp

from .homeplusconst import HOMES_STATUS_URL


class HomePlusModule:
    """Base Class representing a "module", i.e a Home+ device such as a plug, a light or a remote.

    Attributes:
        plant (HomePlusPlant): Plant that holds this module
        id (str): Unique identifier of the module
        name (str): Name of the module
        hw_type (str): Hardware type(?) of the module (NLP, NLT, NLF)
        device (str): Type of the device (plug, light, remote)
        fw (str, optional): Firmware(?) of the module. Defaults to an empty string.
        type (str, optional): Additional type information of the module. Defaults to an empty string.
        reachable (bool, optional): True if the module is reachable and False if it is not. Defaults to False.
        statusUrl (str): URL of the API endpoint that returns the status of the module
    """

    def __init__(self, plant, id, name, hw_type, device, bridge, fw="", type="", reachable=False):
        """HomePlusModule Constructor

        Args:
            plant (HomePlusPlant): Plant that holds this module
            id (str): Unique identifier of the module
            name (str): Name of the module
            hw_type (str): Hardware type(?) of the module (NLP, NLT, NLF)
            device (str): Type of the device (plug, light, remote)
            bridge (str): Unique identifier of the bridge that controls this module
            fw (str, optional): Firmware(?) of the module. Defaults to an empty string.
            type (str, optional): Additional type information of the module. Defaults to an empty string.
            reachable (bool, optional): True if the module is reachable and False if it is not. Defaults to False.
        """
        self.plant = plant
        self.id = id
        self.name = name
        self.hw_type = hw_type
        self.device = device
        self.reachable = reachable
        self.fw = fw
        self.type = type
        self.bridge = bridge
        self.statusUrl = HOMES_STATUS_URL

    def __str__(self):
        """Return the string representing this module"""
        return f"Home+ Module: device->{self.device}, name->{self.name}, id->{self.id}, reachable->{self.reachable}, bridge->{self.bridge}"

    @property
    def logger(self):
        """Return logger of the Home+ Control Module"""
        return logging.getLogger(__name__)

    def update_state(self, module_data):
        """Update the internal state of the module from the input JSON data.

        Args:
            module_data (json): JSON data of the module state
        """
        self.reachable = module_data.get("reachable") is True
        self.fw = module_data.get("firmware_revision")

    async def get_status_update(self):
        """Get the current status of the module by calling the corresponding API method
        located at the URL in the `statusUrl` attributes.

        Returns:
            dict: JSON representation of the module's status.
        """
        oauth_client = self.plant.oauth_client
        try:
            response = await oauth_client.get_request(self.statusUrl, {"home_id": self.plant.id})
        except aiohttp.ClientResponseError:
            self.logger.error("HTTP client response error when update module status")
        else:
            response_body = await response.json()
            all_module_status = response_body["body"]["home"]["modules"]
            module_data = {}
            for module in all_module_status:
                if module["id"] == self.id:
                    module_data = module
            self.update_state(module_data)
        return module_data
