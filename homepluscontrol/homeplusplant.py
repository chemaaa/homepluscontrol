import json
import aiohttp
from .authentication import EliotOAuth2Async
from .homeplusmodule import HomePlusModule
from .homepluslight import HomePlusLight
from .homeplusplug import HomePlusPlug
from .homeplusremote import HomePlusRemote

PLANT_TOPOLOGY_BASE_URL='https://api.developer.legrand.com/hc/api/v1.0/plants/'
PLANT_TOPOLOGY_RESOURCE='/topology'

class HomePlusPlant:
    """Class representing a "plant", i.e a Home or Environment containing Home+ devices"""

    def __init__(self, id, name, country, oauth_client: EliotOAuth2Async):
        self.id = id
        self.name = name
        self.country = country
        self.oauth_client = oauth_client
        self.modules = {}

    def __str__(self):
        return f'Home+ Plant: name->{self.name}, id->{self.id}, country->{self.country}'

    async def refresh_topology(self):
        self.topology = json.loads('{"plant": { } }')
        try:        
             response = await self.oauth_client.get_request(PLANT_TOPOLOGY_BASE_URL + self.id + PLANT_TOPOLOGY_RESOURCE)
        except aiohttp.ClientResponseError as err:
            print(err)
        else:
            self.topology = await response.json()

    async def refresh_module_status(self):
        self.module_status = json.loads('{"modules": { } }')
        try:        
             response = await self.oauth_client.get_request(PLANT_TOPOLOGY_BASE_URL + self.id)
        except aiohttp.ClientResponseError as err:
            print(err)
        else:
            self.module_status = await response.json()

    async def update_topology_and_modules(self):
        await self.refresh_topology()
        await self.refresh_module_status()

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
        if input_module['device'] == 'light':
            self.modules[input_module['id']] = HomePlusLight(plant=self, id=input_module['id'], device=input_module['device'], name=input_module['name'], hw_type=input_module['hw_type'])
        elif input_module['device'] == 'plug':
            self.modules[input_module['id']] = HomePlusPlug(plant=self, id=input_module['id'], device=input_module['device'], name=input_module['name'], hw_type=input_module['hw_type'])
        elif input_module['device'] == 'remote':
            self.modules[input_module['id']] = HomePlusRemote(plant=self, id=input_module['id'], device=input_module['device'], name=input_module['name'], hw_type=input_module['hw_type'])
        else:
            self.modules[input_module['id']] = HomePlusModule(plant=self, id=input_module['id'], device=input_module['device'], name=input_module['name'], hw_type=input_module['hw_type'])

    def _update_module(self, input_module):
        u_module = self.modules[input_module['id']]
        u_module.device = input_module['device']
        u_module.name = input_module['name']
        u_module.hw_type = input_module['hw_type']

    def _update_module_base_status(self, curr_module_id, input_module):
        u_module=self.modules[curr_module_id]
        u_module.fw = input_module['fw']
        u_module.reachable = input_module['reachable'] == True

    def _update_interactive_module_status(self, curr_module_id, input_module):
        u_module=self.modules[curr_module_id]
        u_module.status = input_module['status']

    def _update_remote_status(self, curr_module_id, input_module):
        u_module=self.modules[curr_module_id]
        u_module.battery = input_module['battery']