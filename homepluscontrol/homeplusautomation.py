import aiohttp

from .homeplusmodule import HomePlusModule


class HomePlusAutomation(HomePlusModule):
    """Class that represents a Home+ Automation Module.

    This class extends the HomePlusModule base class.

    Attributes:
        level (int): The automation's position level (as an integer value from 0 to 100).
    """

    MODULE_BASE_URL = "https://api.developer.legrand.com/hc/api/v1.0/automation/automation/addressLocation/plants/"
    """API endpoint for the Home+ Automation status """

    OPEN_FULL = 100
    """Level value that represents a fully open cover."""

    CLOSED_FULL = 0
    """Level value that represents a fully closed cover."""

    def __init__(
        self, plant, id, name, hw_type, device, fw="", type="", reachable=False
    ):
        """HomePlusAutomation Constructor

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
        super().__init__(plant, id, name, hw_type, device, fw, type, reachable)
        self.level = None
        self.build_status_url(HomePlusAutomation.MODULE_BASE_URL)

    def __str__(self):
        """ Return the string representing this module """
        return f"Home+ Automation Module: device->{self.device}, name->{self.name}, id->{self.id}, reachable->{self.reachable}, level->{self.level}"

    async def open(self):
        """ Open the automation module """
        self.set_level(HomePlusAutomation.OPEN_FULL)

    async def close(self):
        """ Close the automation module """
        self.set_level(HomePlusAutomation.CLOSED_FULL)

    async def set_level(self, desired_level):
        """Set the level of the automation module."""
        if desired_level < 0:
            desired_level = 0
        if desired_level > 100:
            desired_level = 100

        if await self.post_status_update(desired_level):
            self.level = desired_level

    async def post_status_update(self, desired_level):
        """Call the API method to act on the module's status.

        Args:
            desired_level (int): Level value to be set on the automation.

        Returns:
            bool: True if the API update request was successful; False otherwise.
        """
        oauth_client = self.plant.oauth_client
        update_status_result = False

        desired_level_data = '{ "ids": ["string"], "level":' + str(desired_level) + '}'
        try:
            response = await oauth_client.post_request(
                self.statusUrl, data=desired_level_data
            )
        except aiohttp.ClientResponseError as err:
            self.logger.error(
                "HTTP client response error when posting module status"
            )
        else:
            update_status_result = True
        return update_status_result

    async def get_status_update(self):
        """Get the current status of the module by calling the corresponding API method.

        Returns:
            dict: JSON representation of the module's status.
        """
        module_data = await super().get_status_update()
        self.level = module_data["level"]
        return module_data