import aiohttp
import json
import logging
from .authentication import HomePlusOAuth2Async
from .homeplusmodule import HomePlusModule
from .homepluslight import HomePlusLight
from .homeplusplug import HomePlusPlug
from .homeplusremote import HomePlusRemote

PLANT_TOPOLOGY_BASE_URL='https://api.developer.legrand.com/hc/api/v1.0/plants/'
""" API endpoint for the Home+ plant information. """

PLANT_TOPOLOGY_RESOURCE='/topology'
""" Path to the Home+ plant topology information. """

class HomePlusPlant:
    """Class representing a "plant", i.e a Home or Environment containing Home+ devices
    
    Attributes:
        id (str): Unique identifier of the plant.
        name (str): Name of the plant.
        country (str): Two-letter country code where the plant is located.
        oauth_client (HomePlusOAuth2Async): Authentication client to make request to the REST API.
        modules (dict): Dictionary containing the information of all modules in the plant.
        topology (dict): JSON representation of the plant's topology as returned by the API
        module_status (dict): JSON representation of the plant modules' status as returned by the API
    """

    def __init__(self, id, name, country, oauth_client: HomePlusOAuth2Async):
        """ HomePlusPlant Constructor 
        
        Args:
            id (str): Unique identifier of the plant.
            name (str): Name of the plant.
            country (str): Two-letter country code where the plant is located.
            oauth_client (HomePlusOAuth2Async): Authentication client to make request to the REST API.
        """
        self.id = id
        self.name = name
        self.country = country
        self.oauth_client = oauth_client
        self.modules = {}

    def __str__(self):
        """ Return the string representing this plant """
        return f'Home+ Plant: name->{self.name}, id->{self.id}, country->{self.country}'

    def logger(self):
        """Return logger of the plant."""
        return logging.getLogger(__name__)

    async def refresh_topology(self):
        """ Makes a call to the API to refresh the topology information of the plant into attribute `topology`.
        The topology provides information about the plants ambients/rooms and the modules within them.

        At this time, the plant topology is only used to extract the module data.
        TODO: Handle ambients/rooms
        """
        self.topology = json.loads('{"plant": { } }')
        try:        
             response = await self.oauth_client.get_request(PLANT_TOPOLOGY_BASE_URL + self.id + PLANT_TOPOLOGY_RESOURCE)
        except aiohttp.ClientResponseError as err:
            logger.exception("HTTP client response error when refreshing plant topology")
        else:
            self.topology = await response.json()

    async def refresh_module_status(self):
        """ Makes a call to the API to refresh the status of all modules in the plant into attribute `module_status`.
        The module status provides information about the modules current status, eg. reachability, on/off, battery, consumption.

        TODO: Handle consumptions
        """
        self.module_status = json.loads('{"modules": { } }')
        try:        
             response = await self.oauth_client.get_request(PLANT_TOPOLOGY_BASE_URL + self.id)
        except aiohttp.ClientResponseError as err:
            logger.exception("HTTP client response error when refreshing module status")
        else:
            self.module_status = await response.json()

    async def update_topology_and_modules(self):
        """ Convenience method that first refreshes the plant's topology information and then refreshes
        the status of all modules in that topology.
        """
        await self.refresh_topology()
        await self.refresh_module_status()
        self._parse_topology_and_modules()

    def _parse_topology_and_modules(self):
        """ Auxiliary method that parses the data returned by the API and converts it into a dictionary
        of modules that is stored in the attribute `modules`.
        """
        # The plant modules come from two distinct elements of the topology - the ambients and the modules
        flat_modules = []
        for ambient in self.topology['plant']['ambients']:
            for module in ambient['modules']:
                flat_modules.append(module)

        for module in self.topology['plant']['modules']:
            flat_modules.append(module)

        for module in flat_modules:
            # Check if the module already exists in the module dict of this plant
            if module['id'] in self.modules:
                self._update_module(module)
            else:
                self._create_module(module)

        # With the modules identified and created, we update their status from the module_status property
        for m in self.module_status['modules']['lights']:
            module_id = m['sender']['plant']['module']['id']
            self._update_module_base_status(module_id, m)
            self._update_interactive_module_status(module_id, m)

        for m in self.module_status['modules']['plugs']:
            module_id = m['sender']['plant']['module']['id']
            self._update_module_base_status(module_id, m)
            self._update_interactive_module_status(module_id, m)

        for m in self.module_status['modules']['remotes']:
            module_id = m['sender']['plant']['module']['id']
            self._update_module_base_status(module_id, m)
            self._update_remote_status(module_id, m)
        
    def _create_module(self, input_module):
        """ 'Factory' method of specific Home+ Control modules depending on their type that adds the new module to the attribute `modules`.
        
        Args:
            input_module (dict): Dictionary representing the JSON structure of a module as returned by the API.
        """
        if input_module['device'] == 'light':
            self.modules[input_module['id']] = HomePlusLight(plant=self, id=input_module['id'], device=input_module['device'], name=input_module['name'], hw_type=input_module['hw_type'])
        elif input_module['device'] == 'plug':
            self.modules[input_module['id']] = HomePlusPlug(plant=self, id=input_module['id'], device=input_module['device'], name=input_module['name'], hw_type=input_module['hw_type'])
        elif input_module['device'] == 'remote':
            self.modules[input_module['id']] = HomePlusRemote(plant=self, id=input_module['id'], device=input_module['device'], name=input_module['name'], hw_type=input_module['hw_type'])
        else:
            self.modules[input_module['id']] = HomePlusModule(plant=self, id=input_module['id'], device=input_module['device'], name=input_module['name'], hw_type=input_module['hw_type'])

    def _update_module(self, input_module):
        """ Update the information of an existing module instance in the plant, based on the latest input data.

        Args:
            input_module (dict): Dictionary representing the JSON structure of a module as returned by the API. This 
                                 contains the latest module data that will be updated into the existing module instance.            
        """
        u_module = self.modules[input_module['id']]
        u_module.device = input_module['device']
        u_module.name = input_module['name']
        u_module.hw_type = input_module['hw_type']

    def _update_module_base_status(self, curr_module_id, input_module):
        """ Update the basic information of an existing module instance in the plant.

        Args:
            curr_module_id (str): Identifier of the existing module that is to be updated.
            input_module (dict): Dictionary representing the JSON structure of a module as returned by the API. This 
                                 contains the latest module data that will be updated into the existing module instance.            
        """
        u_module=self.modules[curr_module_id]
        u_module.fw = input_module['fw']
        u_module.reachable = input_module['reachable'] == True

    def _update_interactive_module_status(self, curr_module_id, input_module):
        """ Update the information of an existing interactive module instance in the plant.
        This method basically updates the status (on or off) of the interactive module.

        Args:
            curr_module_id (str): Identifier of the existing interactive module that is to be updated.
            input_module (dict): Dictionary representing the JSON structure of a module as returned by the API. This 
                                 contains the latest module data that will be updated into the existing module instance.            
        """
        u_module=self.modules[curr_module_id]
        u_module.status = input_module['status']

    def _update_remote_status(self, curr_module_id, input_module):
        """ Update the information of an existing remote module instance in the plant.
        This method basically updates the battery status of the remote module.

        Args:
            curr_module_id (str): Identifier of the existing remote module that is to be updated.
            input_module (dict): Dictionary representing the JSON structure of a module as returned by the API. This 
                                 contains the latest module data that will be updated into the existing module instance.            
        """
        u_module=self.modules[curr_module_id]
        u_module.battery = input_module['battery']