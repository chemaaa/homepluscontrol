import time
from .authentication import EliotOAuth2
import json
import aiohttp

class HomePlusModule:
    """Base Class representing a "module", i.e a Home+ device such as a plug, a light or a remote"""
    
    def __init__(self, plant, id, name, hw_type, device, fw='', type='', reacheable = False):
        self.plant = plant
        self.id = id
        self.name = name
        self.hw_type = hw_type
        self.device = device
        self.reachable = reacheable
        self.fw = fw
        self.type = type
        
        self.build_status_url('')

    def __str__(self):
        return f'Home+ Module: device->{self.device}, name->{self.name}, id->{self.id}, reachable->{self.reachable}'

    def build_status_url(self, base_url):
        self.statusUrl = base_url + self.plant.id + '/modules/parameter/id/value/' + self.id

    async def get_status_update(self):
        oauth_client = self.plant.oauth_client
        status_result =  json.loads('{"modules": { } }')
        try:        
            response = await oauth_client.get_request(self.statusUrl)
        except aiohttp.ClientResponseError as err:
            print(err)
        else:            
            status_result = await response.json()        
            module_key = list(status_result)[0]
            module_data = status_result[module_key][0]
            self.reachable = module_data['reachable'] == True
            self.fw = module_data['fw']
        return module_data