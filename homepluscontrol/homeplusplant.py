import json
import logging

import aiohttp

from .homeplusconst import HOMES_DATA_URL, HOMES_STATUS_URL, PRODUCT_TYPES
from .authentication import AbstractHomePlusOAuth2Async
from .homeplusmodule import HomePlusModule
from .homepluslight import HomePlusLight
from .homeplusplug import HomePlusPlug
from .homeplusremote import HomePlusRemote
from .homeplusautomation import HomePlusAutomation

MODULE_CLASSES = {
    "light": HomePlusLight,
    "plug": HomePlusPlug,
    "remote": HomePlusRemote,
    "automation": HomePlusAutomation,
}


class HomePlusPlant:
    """Class representing a "home", i.e a Home or Environment containing Home+ devices

    Attributes:
        id (str): Unique identifier of the home.
        name (str): Name of the home.
        country (str): Two-letter country code where the home is located.
        oauth_client (AbstractHomePlusOAuth2Async): Authentication client to make requests to the REST API.
        modules (dict): Dictionary containing the information of all modules in the home.
        home_data (dict): JSON representation of the home's data as returned by the API
        module_status (dict): JSON representation of the home modules' status as returned by the API
    """

    def __init__(self, id, home_data, oauth_client: AbstractHomePlusOAuth2Async):
        """HomePlusPlant Constructor

        Args:
            id (str): Unique identifier of the home.
            home_data (dict): JSON representation of the home's data as returned by the API.
            country (str): Two-letter country code where the home is located.
            oauth_client (AbstractHomePlusOAuth2Async): Authentication client to make request to the REST API.
        """
        self.id = id
        self.oauth_client = oauth_client
        self.modules = {}
        self.module_status = json.loads("[ ]")

        self._set_home_data(home_data)
        self._parse_home_data(home_data)

    def __str__(self):
        """Return the string representing this home"""
        return f"Home+ Home: name->{self.name}, id->{self.id}, country->{self.country}"

    @property
    def logger(self):
        """Return logger of the home."""
        return logging.getLogger(__name__)

    async def update_home_data(self, input_home_data=None):
        """Method that optionally refreshes the home's topology information through an API call
        and then parses the modules contained in that topology into the object's inner map.

        This method call on its own will not refresh the status of the modules.

        Args:
            input_home_data (dict): Dictionary representing the JSON structure of the home as returned by the API.
                                    If absent, an API call will be made to obtain this data.
        """
        if input_home_data is None:
            new_home_data = await self._refresh_home_data()
        else:
            new_home_data = input_home_data

        self._set_home_data(new_home_data)
        self._parse_home_data(new_home_data)

    async def update_module_status(self, input_module_status=None):
        """Method that optionally refreshes the information of the modules' status through an API call
        and then parses the status information into the modules of the object's inner map.

        This method call on its own will not refresh the module topology of the home so modules that are no longer
        present in the home will remain with their last known status, while new modules that may have been added
        to the topology will not be reflected in it just yet.

        Args:
            input_module_status (dict): Dictionary representing the JSON structure of the home's module status as returned
                                        by the API. If absent, an API call will be made to obtain this data.
        """
        if input_module_status is None:
            new_module_status = await self._refresh_module_status()
        else:
            new_module_status = input_module_status

        self._parse_module_status(new_module_status)

    async def update_home_data_and_modules(self, input_home_data=None, input_module_status=None):
        """Convenience method that calls the `update_home_data` and `update_modules_status` methods in sequence so as
        to update the home's topology information and then refresh the status of all modules in that topology.

        This implies at least 1 API call and will produce an up-to-date view of the home in the inner map of modules.

        Args:
            input_home_data (dict): Dictionary representing the JSON structure of the home as returned by the API.
                                    If absent, an API call will be made to obtain this data.
            input_module_status (dict): Dictionary representing the JSON structure of the home's module status as returned
                                        by the API. If absent, an API call will be made to obtain this data.
        """
        await self.update_home_data(input_home_data)
        await self.update_module_status(input_module_status)

    def _set_home_data(self, input_home_data):
        """Update the home information from the input home data JSON object.

        Args:
            input_home_data (dict): Dictionary representing the JSON structure of the home as returned by the API.
        """
        self.name = input_home_data.get("name", "UNKNOWN")
        self.country = input_home_data.get("country", "XX")
        self.home_data = input_home_data

    async def _refresh_home_data(self):
        """Makes a call to the API to refresh the information of the home into attribute `home_data`.

        At this time, the home topology is only used to extract the module data.
        TODO: Handle rooms/schedules

        Returns:
            dict: Dictionary representing the JSON structure of the home as returned by the API.
        """
        new_home_data = self.home_data
        try:
            response = await self.oauth_client.get_request(HOMES_DATA_URL)
        except aiohttp.ClientResponseError:
            self.logger.error("HTTP client response error when refreshing home's data")
        else:
            response_body = await response.json()
            for home_data in response_body["body"]["homes"]:
                if home_data["id"] == self.id:
                    new_home_data = home_data
                    self.home_data = new_home_data
        return new_home_data

    async def _refresh_module_status(self):
        """Makes a call to the API to refresh the status of all modules in the home into attribute `module_status`.
        The module status provides information about the modules current status, eg. reachability, on/off,
        battery, consumption.

        TODO: Handle consumptions

        Returns:
            dict: Dictionary representing the JSON structure of the home's module status as returned by the API.
        """
        new_module_status = self.module_status
        try:
            response = await self.oauth_client.get_request(HOMES_STATUS_URL, {"home_id": self.id})
        except aiohttp.ClientResponseError:
            self.logger.error("HTTP client response error when refreshing module status")
        else:
            response_body = await response.json()
            new_module_status = response_body["body"]["home"]["modules"]
            self.module_status = new_module_status
        return new_module_status

    def _parse_home_data(self, input_home_data):
        """Auxiliary method to parse the home data returned by the API.

        Args:
            input_home_data (dict): Dictionary representing the JSON structure of the home as returned by the API.
        """
        # Extract the home's modules from the topology data structure.
        flat_modules = {}
        for module in input_home_data.get("modules", []):
            flat_modules[module["id"]] = module

        input_module_ids = set(flat_modules)
        current_module_ids = set(self.modules)

        # New modules
        for new_module_id in input_module_ids.difference(current_module_ids):
            self._create_module(flat_modules[new_module_id])
        # Modules that already existed
        for update_module_id in current_module_ids.intersection(input_module_ids):
            self._update_module(flat_modules[update_module_id])
        # Modules no longer there
        for delete_module_id in current_module_ids.difference(input_module_ids):
            self.modules.pop(delete_module_id, None)

    def _parse_module_status(self, input_module_status):
        """Auxiliary method to parse the module status data returned by the API.

        It is assumed that the home topology is up to date - this method will only search for the module status
        of those modules that have been parsed in the topology data.

        Args:
            input_module_status (dict): Dictionary representing the JSON structure of the home's module status as returned
                                        by the API.
        """
        # With the modules identified in the module_status information,
        # we update their status into the modules map of this home object
        input_module_ids = set()

        for m_json in input_module_status:
            module_id = m_json["id"]
            input_module_ids.add(module_id)
            if module_id in self.modules:
                self.modules[module_id].update_state(m_json)

        # Check whether any existing modules in the topology have no module status info
        # and if that is the case, then we mark them as unreachable
        for existing_id in set(self.modules).difference(input_module_ids):
            self.modules[existing_id].reachable = False

    def _create_module(self, input_module):
        """'Factory' method of specific Home+ Control modules depending on their type that adds the new module
        to the attribute `modules`.

        Args:
            input_module (dict): Dictionary representing the JSON structure of a module as returned by the API.
        """
        module_product_type = PRODUCT_TYPES.get(input_module["type"])
        module_class = MODULE_CLASSES.get(module_product_type, HomePlusModule)

        self.modules[input_module["id"]] = module_class(
            plant=self,
            id=input_module["id"],
            device=module_product_type,
            name=input_module["name"],
            hw_type=input_module["type"],
            type=input_module.get("appliance_type"),
            bridge=input_module.get("bridge"),
        )

    def _update_module(self, input_module):
        """Update the information of an existing module instance in the home, based on the latest input data.

        Args:
            input_module (dict): Dictionary representing the JSON structure of a module as returned by the API. This
                                 contains the latest module data that will be updated into the existing module instance.
        """
        u_module = self.modules[input_module["id"]]

        # If the device type has changed, then we have to re-create the object of the correct class
        # This should not really happen if the IDs in the Legrand platform are really unique.
        if input_module["type"] != u_module.hw_type:
            self._create_module(input_module)
        else:
            u_module.name = input_module["name"]
            u_module.bridge = input_module.get("bridge")
