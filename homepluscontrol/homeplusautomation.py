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

    STOP_MOTION = -1
    """Level value to send to the API to make the automation stop."""

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

    def update_state(self, module_data):
        """Update the internal state of the module from the input JSON data.

        Args:
            module_data (json): JSON data of the module state
        """
        super().update_state(module_data)
        self.level = module_data["level"]

    async def open(self):
        """ Open the automation module.

        This method will indicate the automation to go to the fully open position.
        """
        await self.set_level(HomePlusAutomation.OPEN_FULL)

    async def close(self):
        """ Close the automation module.

        This method will indicate the automation to go to the fully closed position.
        """
        await self.set_level(HomePlusAutomation.CLOSED_FULL)

    async def stop(self):
        """Stop the motion of the automation module."""
        await self.set_level(HomePlusAutomation.STOP_MOTION)

    async def set_level(self, desired_level):
        """Set the level of the automation module."""
        if desired_level < 0 and desired_level != -1:
            desired_level = HomePlusAutomation.CLOSED_FULL
        if desired_level > 100:
            desired_level = HomePlusAutomation.OPEN_FULL

        if await self.post_status_update(desired_level):
            if desired_level != HomePlusAutomation.STOP_MOTION:
                self.level = desired_level  # Not being stopped, so assume final level is the requested level
            else:
                await self.get_status_update()  # Stop command issued - need to read the final level

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
            await oauth_client.post_request(
                self.statusUrl,
                data=desired_level_data,
                headers={"Content-Type": "application/json"},
            )
        except aiohttp.ClientResponseError:
            self.logger.error(
                "HTTP client response error when posting module status"
            )
        else:
            update_status_result = True
        return update_status_result
