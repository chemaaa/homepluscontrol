from .homeplusmodule import HomePlusModule
from .authentication import EliotOAuth2
import aiohttp

class HomePlusInteractiveModule(HomePlusModule):
    """Base Class for Home+ modules that are interactive, i.e a Home+ device that accepts commands to update 
    its status, such as a plug or a light"""
    
    MODULE_BASE_URL='https://api.developer.legrand.com/hc/api/v1.0/dummy'
    STATUS_ON = {'status':'on'}
    STATUS_OFF = {'status':'off'}

    def __init__(self, plant, id, name, hw_type, device, fw='', type='', reacheable = False):
        super().__init__(plant, id, name, hw_type, device, fw, type, reacheable)
        self.status = ''    

    def __str__(self):
        return f'Home+ Interactive Module: device->{self.device}, name->{self.name}, id->{self.id}, reachable->{self.reachable}, status->{self.status}'

    async def turn_on(self):
        if await self.post_status_update(HomePlusInteractiveModule.STATUS_ON):
            self.status = 'on'

    async def turn_off(self):
        if await self.post_status_update(HomePlusInteractiveModule.STATUS_OFF):
            self.status = 'off'
    
    async def toggle_status(self):
        desired_end_status = 'off'
        if self.status == 'off':
            desired_end_status = 'on'
        if await self.post_status_update( {'status': desired_end_status} ):
            self.status = desired_end_status

    async def post_status_update(self, desired_end_status):
        oauth_client = self.plant.oauth_client
        update_status_result = False
        try:        
            response = await oauth_client.post_request(self.statusUrl, data=desired_end_status)
        except aiohttp.ClientResponseError as err:
            print(err)
        else:
            update_status_result = True        
        return update_status_result

    async def get_status_update(self):
        module_data = await super().get_status_update()
        self.status = module_data['status']
        return module_data