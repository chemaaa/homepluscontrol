from .homeplusmodule import HomePlusModule


class HomePlusRemote(HomePlusModule):
    """Class that represents a Home+ Remote Module, i.e. a switch that is wireless and configured
    to control specific modules in the plant

    This class extends the HomePlusModule base class. The remote is not an interactive module.

    Attributes:
        battery: state of charge of the module's battery (full/high/medium/low/very_low).
        battery_level: state of charge of the module's battery
    """

    def __init__(self, plant, id, name, hw_type, device, bridge, fw="", type="", reachable=False):
        """HomePlusRemote Constructor

        Args:
            plant (HomePlusPlant): Plant that holds this module
            id (str): Unique identifier of the module
            name (str): Name of the module
            hw_type (str): Hardware/product of the module (NLP, NLT, NLF)
            device (str): Type of the device (plug, light, remote)
            bridge (str): Unique identifier of the bridge that controls this module
            fw (str, optional): Firmware revision of the module. Defaults to an empty string.
            type (str, optional): Additional type information of the module. Defaults to an empty string.
            reachable (bool, optional): True if the module is reachable and False if it is not. Defaults to False.
        """
        super().__init__(plant, id, name, hw_type, device, bridge, fw, type, reachable)
        self.battery = ""
        self.battery_level = ""

    def __str__(self):
        """Return the string representing this module"""
        return f"Home+ Remote: device->{self.device}, name->{self.name}, id->{self.id}, reachable->{self.reachable}, battery->{self.battery}, battery_level->{self.battery_level}, bridge->{self.bridge}"

    def update_state(self, module_data):
        """Update the internal state of the module from the input JSON data.

        Args:
            module_data (json): JSON data of the module state
        """
        super().update_state(module_data)
        self.battery = module_data.get("battery_state")
        self.battery_level = module_data.get("battery_level")
