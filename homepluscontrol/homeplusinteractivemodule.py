import logging

import aiohttp

from .homeplusmodule import HomePlusModule


class HomePlusInteractiveModule(HomePlusModule):
    """Base Class for Home+ modules that are interactive, i.e a Home+ device that accepts commands to update 
    its status, such as a plug or a light

    This class extends the HomePlusModule base class.

    Attributes:
        status (str): The module can have status = 'on' or status = 'off'
    """
    
    MODULE_BASE_URL='https://api.developer.legrand.com/hc/api/v1.0/dummy'
    """ Dummy endpoint for this module's status - has to be set by the inheriting classes."""

    STATUS_ON = {'status':'on'}
    """ Data that is to be sent to the API to set the device to an 'on' state."""

    STATUS_OFF = {'status':'off'}
    """ Data that is to be sent to the API to set the device to an 'on' state."""

    def __init__(self, plant, id, name, hw_type, device, fw='', type='', reachable = False):
        """ HomePlusInteractiveModule Constructor 
        
        Args:
            plant (HomePlusPlant): Plant that holds this module
            id (str): Unique identifier of the module
            name (str): Name of the module
            hw_type (str): Hardware type(?) of the module (NLP, NLT, NLF)
            device (str): Type of the device (plug, light, remote)
            fw (str, optional): Firware(?) of the module. Defaults to an empty string.
            type (str, optional): Additional type information of the module. Defaults to an empty string.
            reachable (bool, optional): True if the module is reachable and False if it is not. Defaults to False.
        """        
        super().__init__(plant, id, name, hw_type, device, fw, type, reachable)
        self.status = ''    

    def __str__(self):
        """ Return the string representing this module """
        return f'Home+ Interactive Module: device->{self.device}, name->{self.name}, id->{self.id}, reachable->{self.reachable}, status->{self.status}'

    async def turn_on(self):
        """ Turn on this interactive module """
        if await self.post_status_update(HomePlusInteractiveModule.STATUS_ON):
            self.status = 'on'

    async def turn_off(self):
        """ Turn off this interactive module """
        if await self.post_status_update(HomePlusInteractiveModule.STATUS_OFF):
            self.status = 'off'
    
    async def toggle_status(self):
        """ Toggle the state of this interactive module, i.e. if the module is on, the method call turns it off.
        If the module is off, the method call turns it on.
        """
        desired_end_status = 'off'
        if self.status == 'off':
            desired_end_status = 'on'
        if await self.post_status_update( {'status': desired_end_status} ):
            self.status = desired_end_status

    async def post_status_update(self, desired_end_status):
        """ Call the API method to act on the module's status. 

        Args: 
            desired_end_status (dict): One of the two class attributes (STATUS_ON and STATUS_OFF) 
                                       that are defined to set the status ON or OFF.

        Returns:
            bool: True if the API update request was successful; False otherwise.
        """
        oauth_client = self.plant.oauth_client
        update_status_result = False
        try:        
            response = await oauth_client.post_request(self.statusUrl, data=desired_end_status)
        except aiohttp.ClientResponseError as err:
            self.logger.error("HTTP client response error when posting module status")
        else:
            update_status_result = True        
        return update_status_result

    async def get_status_update(self):
        """ Get the current status of the module by calling the corresponding API method. 
        
        Returns:
            dict: JSON representation of the module's status.
        """
        module_data = await super().get_status_update()
        self.status = module_data['status']
        return module_data