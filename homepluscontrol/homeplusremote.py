from .homeplusmodule import HomePlusModule

class HomePlusRemote(HomePlusModule):
    """Home+ Remote Module, i.e. a switch that is wireless and configured to control specific modules
    in the plant"""

    MODULE_BASE_URL = 'https://api.developer.legrand.com/hc/api/v1.0/remote/remote/addressLocation/plants/'

    def __init__(self, plant, id, name, hw_type, device, fw='', type='', reacheable = False):
        super().__init__(plant, id, name, hw_type, device, fw, type, reacheable)
        self.battery = ''

    def __str__(self):
        return f'Home+ Remote: device->{self.device}, name->{self.name}, id->{self.id}, reachable->{self.reachable}, battery->{self.battery}'

    async def get_status_update(self):
        module_data = await super().get_status_update()
        self.battery = module_data['battery']
        return module_data