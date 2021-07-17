import json
import logging

import aiohttp


class HomePlusModule:
    """Base Class representing a "module", i.e a Home+ device such as a plug, a light or a remote.

    Attributes:
        plant (HomePlusPlant): Plant that holds this module
        id (str): Unique identifier of the module
        name (str): Name of the module
        hw_type (str): Hardware type(?) of the module (NLP, NLT, NLF)
        device (str): Type of the device (plug, light, remote)
        fw (str, optional): Firware(?) of the module. Defaults to an empty string.
        type (str, optional): Additional type information of the module. Defaults to an empty string.
        reachable (bool, optional): True if the module is reachable and False if it is not. Defaults to False.
        statusUrl (str): URL of the API endpoint that returns the status of the module
    """

    def __init__(
        self, plant, id, name, hw_type, device, fw="", type="", reachable=False
    ):
        """HomePlusModule Constructor

        Args:
            plant (HomePlusPlant): Plant that holds this module
            id (str): Unique identifier of the module
            name (str): Name of the module
            hw_type (str): Hardware type(?) of the module (NLP, NLT, NLF)
            device (str): Type of the device (plug, light, remote)
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

        self.build_status_url("")

    def __str__(self):
        """ Return the string representing this module """
        return f"Home+ Module: device->{self.device}, name->{self.name}, id->{self.id}, reachable->{self.reachable}"

    @property
    def logger(self):
        """ Return logger of the Home+ Control Module """
        return logging.getLogger(__name__)

    def build_status_url(self, base_url):
        """Build the full API URL that provides the status of the module. The URL is updated into the `statusUrl` attribute

        Args:
            base_url (str): Leftmost part of the URL to which Plant and Module Identifiers are concatenated

        """
        self.statusUrl = (
            base_url + self.plant.id + "/modules/parameter/id/value/" + self.id
        )

    def update_state(self, module_data):
        """Update the internal state of the module from the input JSON data.

        Args:
            module_data (json): JSON data of the module state
        """
        self.reachable = module_data["reachable"] is True
        self.fw = module_data["fw"]

    async def get_status_update(self):
        """Get the current status of the module by calling the corresponding API method
        located at the URL in the `statusUrl` attributes.

        Returns:
            dict: JSON representation of the module's status.
        """
        oauth_client = self.plant.oauth_client
        status_result = json.loads('{"modules": { } }')
        try:
            response = await oauth_client.get_request(self.statusUrl)
        except aiohttp.ClientResponseError:
            self.logger.error(
                "HTTP client response error when update module status"
            )
        else:
            status_result = await response.json()
            module_key = list(status_result)[0]
            module_data = status_result[module_key][0]
            self.update_state(module_data)
        return module_data
