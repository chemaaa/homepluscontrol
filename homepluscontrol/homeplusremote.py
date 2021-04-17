from .homeplusmodule import HomePlusModule


class HomePlusRemote(HomePlusModule):
    """Class that represents a Home+ Remote Module, i.e. a switch that is wireless and configured
    to control specific modules in the plant

    This class extends the HomePlusModule base class. The remote is not an interactive module.

    Attributes:
        battery: level of charge of the module's battery.
    """

    MODULE_BASE_URL = "https://api.developer.legrand.com/hc/api/v1.0/remote/remote/addressLocation/plants/"
    """ API endpoint for the Home+ Remote status """

    def __init__(
        self, plant, id, name, hw_type, device, fw="", type="", reachable=False
    ):
        """HomePlusRemote Constructor

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
        self.battery = ""
        self.build_status_url(HomePlusRemote.MODULE_BASE_URL)

    def __str__(self):
        """ Return the string representing this module """
        return f"Home+ Remote: device->{self.device}, name->{self.name}, id->{self.id}, reachable->{self.reachable}, battery->{self.battery}"

    def update_state(self, module_data):
        """Update the internal state of the module from the input JSON data.

        Args:
            module_data (json): JSON data of the module state
        """
        super().update_state(module_data)
        self.battery = module_data["battery"]
