from .homeplusinteractivemodule import HomePlusInteractiveModule

class HomePlusLight(HomePlusInteractiveModule):
    """Home+ Light Module"""

    MODULE_BASE_URL='https://api.developer.legrand.com/hc/api/v1.0/light/lighting/addressLocation/plants/'

    def __init__(self, plant, id, name, hw_type, device, fw='', type='', reacheable = False):
        super().__init__(plant, id, name, hw_type, device, fw, type, reacheable)
        self.status = ''
        self.build_status_url(HomePlusLight.MODULE_BASE_URL)

    def __str__(self):
        return f'Home+ Light: device->{self.device}, name->{self.name}, id->{self.id}, reachable->{self.reachable}, status->{self.status}'

