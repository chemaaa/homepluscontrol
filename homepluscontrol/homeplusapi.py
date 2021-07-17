import aiohttp
import logging

import time

from .authentication import AbstractHomePlusOAuth2Async
from .homeplusplant import HomePlusPlant, PLANT_TOPOLOGY_BASE_URL
from .homeplusinteractivemodule import HomePlusInteractiveModule

CONF_PLANT_UPDATE_INTERVAL = "plant_update_interval"
CONF_PLANT_TOPOLOGY_UPDATE_INTERVAL = "plant_topology_update_interval"
CONF_MODULE_STATUS_UPDATE_INTERVAL = "module_status_update_interval"

# The Legrand Home+ Control API has very limited request quotas - at the time of writing, it is
# limited to 500 calls per day (resets at 00:00) - so we want to keep updates to a minimum.
DEFAULT_UPDATE_INTERVALS = {
    # Seconds between API checks for plant information updates. This is expected to change very
    # little over time because a user's plants (homes) should rarely change.
    CONF_PLANT_UPDATE_INTERVAL: 7200,  # 120 minutes
    # Seconds between API checks for plant topology updates. This is expected to change  little
    # over time because the modules in the user's plant should be relatively stable.
    CONF_PLANT_TOPOLOGY_UPDATE_INTERVAL: 3600,  # 60 minutes
    # Seconds between API checks for module status updates. This can change frequently so we
    # check often
    CONF_MODULE_STATUS_UPDATE_INTERVAL: 300,  # 5 minutes
}


class HomePlusControlApiError(Exception):
    """General HomePlusControlApi error occurred."""


class HomePlusControlAPI(AbstractHomePlusOAuth2Async):
    """Presents a unique API to the Home+ Control platform.

    This class is an implementation of the base class AbstractHomePlusOAuth2Async and is intended for the integration
    into Home Assistant.

    This class presents a unified view of the interactive modules that are available in the Home+ Control platform
    through the method `async_get_modules()` and it handles the refresh of the different elements of the plant, topology and
    module status through the provided update intervals.

    This class is still in an abstract form because it does not implement the method `async_get_access_token()`. That
    is provided through the Home Assistant integration.

    Attributes:
        subscription_key (str): Subscription key obtained from the API provider
        oauth_client (:obj:`ClientSession`): aiohttp ClientSession object that handles HTTP async requests
        _plants (dict): Dictionary containing the information of all plants.
        _modules (dict): Dictionary containing the information of all modules in the plants.
        _modules_to_remove (dict): Dictionary containing the information of modules that are no longer in the plants' topology.
        _refresh_intervals (dict): Dictionary of the configured update intervals for plant, topology
                                   and module status information.
    """

    def __init__(
        self,
        subscription_key,
        oauth_client=None,
        update_intervals=DEFAULT_UPDATE_INTERVALS,
    ):
        """HomePlusControlAPI Constructor

        Args:
            subscription_key (str): Subscription key obtained from the API provider
            oauth_client (:obj:`ClientSession`): aiohttp ClientSession object that handles HTTP async requests
            update_intervals (dict): Optional dictionary that contains refresh intervals for the plant, topology
                                     and module status.
        """
        super().__init__(
            subscription_key=subscription_key,
            oauth_client=oauth_client,
        )
        self._plants = {}
        self._modules = {}
        self._modules_to_remove = {}

        self._last_check = {
            CONF_PLANT_UPDATE_INTERVAL: time.monotonic(),
            CONF_PLANT_TOPOLOGY_UPDATE_INTERVAL: -1,
            CONF_MODULE_STATUS_UPDATE_INTERVAL: -1,
        }

        # Set the update intervals
        self._refresh_intervals = {}
        for interval_name in DEFAULT_UPDATE_INTERVALS:
            new_interval_value = update_intervals.setdefault(
                interval_name, DEFAULT_UPDATE_INTERVALS[interval_name]
            )
            self._refresh_intervals[interval_name] = new_interval_value

    @property
    def logger(self):
        """Return logger of the API."""
        return logging.getLogger(__name__)

    async def async_get_modules(self):
        """Retrieve the module information.

        Returns:
            dict: Dictionary of modules across all of the plants keyed by the unique platform identifier.
        """
        await self.async_handle_plant_data()
        return await self.async_handle_module_status()

    async def async_handle_plant_data(self):
        """Recover the plant data for this particular user.

        This will populate the "private" array of plants of this object and will return it.
        It is expected that in most cases, there will only be one plant.

        Returns:
            dict: Dictionary of plants for this user - Keyed by the plant ID. Can be empty if no
                  plants are retrieved.
        """
        # Attempt to recover the plant information from the cache.
        # If it is not there, then we request it from the API and add it.
        # We also refresh from the API if the time has expired.
        if not self._plants or self._should_check(
            CONF_PLANT_UPDATE_INTERVAL,
            self._refresh_intervals[CONF_PLANT_UPDATE_INTERVAL],
        ):
            try:
                result = await self.get_request(
                    PLANT_TOPOLOGY_BASE_URL
                )  # Call the API
                plant_info = await result.json()
            except aiohttp.ClientError as err:
                raise HomePlusControlApiError(
                    "Error retrieving plant information"
                ) from err

            # If all goes well, we update the last check time
            self._last_check[CONF_PLANT_UPDATE_INTERVAL] = time.monotonic()
            self.logger.debug(
                "Obtained plant information from API: %s", plant_info
            )
        else:
            self.logger.debug(
                "Not refreshing data just yet. Obtained plant information from cached info: %s",
                self._plants,
            )
            return self._plants

        # Populate the dictionary of plants
        current_plant_ids = []
        for plant in plant_info["plants"]:
            current_plant_ids.append(plant["id"])
            if plant["id"] in self._plants:
                self.logger.debug(
                    "Plant with id %s is already cached. Only updating the existing data.",
                    plant["id"],
                )
                cur_plant = self._plants.get(plant["id"])
                # We will update the plant info just in case and ensure it has an Api object
                cur_plant.name = plant["name"]
                cur_plant.country = plant["country"]
                if cur_plant.oauth_client is None:
                    cur_plant.oauth_client = self
            else:
                self.logger.debug(
                    "New plant with id %s detected.", plant["id"]
                )
                self._plants[plant["id"]] = HomePlusPlant(
                    plant["id"], plant["name"], plant["country"], self
                )

        # Discard plants that may have disappeared
        plants_to_pop = set(self._plants) - set(current_plant_ids)

        for plant_id in plants_to_pop:
            self.logger.debug(
                "Plant with id %s is no longer present, so remove from cache.",
                plant_id
            )
            self._plants.pop(plant_id, None)

        return self._plants

    async def async_handle_module_status(self):
        """Recover the topology information for the plants defined in this object.

        By requesting the topology of the plant, the system learns about the modules that exist.
        The topology indicates identifiers, type and other device information, but it contains no
        information about the state of the module.

        This method returns the list of modules that will be registered in HomeAssistant.
        At this time the modules that are discovered through this API call are flattened into a
        single data structure.

        Returns:
            dict: Dictionary of modules across all of the plants.
        """
        for plant in self._plants.values():

            if self._should_check(
                CONF_PLANT_TOPOLOGY_UPDATE_INTERVAL,
                self._refresh_intervals[CONF_PLANT_TOPOLOGY_UPDATE_INTERVAL],
            ):
                self.logger.debug(
                    "API update of plant topology for plant %s.", plant.id
                )
                try:
                    await plant.update_topology()  # Call the API
                except Exception as err:
                    self.logger.error(
                        "Error encountered when updating plant topology for plant %s: %s [%s]",
                        plant.id,
                        err,
                        type(err),
                    )
                else:
                    # If all goes well, we update the last check time
                    self._last_check[
                        CONF_PLANT_TOPOLOGY_UPDATE_INTERVAL
                    ] = time.monotonic()

            if self._should_check(
                CONF_MODULE_STATUS_UPDATE_INTERVAL,
                self._refresh_intervals[CONF_MODULE_STATUS_UPDATE_INTERVAL],
            ):
                self.logger.debug(
                    "API update of module status for plant %s.", plant.id
                )
                try:
                    await plant.update_module_status()  # Call the API
                except Exception as err:
                    self.logger.error(
                        "Error encountered when updating plant module status for plant %s: %s [%s]",
                        plant.id,
                        err,
                        type(err),
                    )
                else:
                    # If all goes well, we update the last check time
                    self._last_check[
                        CONF_MODULE_STATUS_UPDATE_INTERVAL
                    ] = time.monotonic()

        return self._update_modules()

    def _should_check(self, check_type, period):
        """Return True if the current monotonic time is > the last check time plus a fixed period.

        Args:
            check_type (str): Type that identifies the timer that has to be used
            period (float): Number of fractional seconds to add to the last check time
        """
        current_time = time.monotonic()
        if (
            self._last_check[check_type] == -1
            or current_time > self._last_check[check_type] + period
        ):
            self.logger.debug(
                "Last check time (%.2f) exceeded by more than %.2f sec - monotonic time %.2f",
                self._last_check[check_type],
                period,
                current_time,
            )
            return True
        return False

    def _update_modules(self):
        """Update the modules based on the collected information in the plant object.

        Returns:
            dict: Dictionary of modules across all of the plants.
        """
        for plant in self._plants.values():
            # Loop through the modules in the plant and we only keep the ones that are "interactive"
            # and can be represented by a switch, i.e. power outlets, micromodules
            # and light switches. All other modules are discarded/ignored.
            current_module_ids = set()
            for module in list(plant.modules.values()):
                if isinstance(module, HomePlusInteractiveModule):
                    current_module_ids.add(module.id)
                    if module.id not in self._modules:
                        self.logger.debug(
                            "Registering Home+ Control module in internal map: %s.",
                            str(module),
                        )
                        self._modules[module.id] = module

            # Discard modules that may have disappeared from the topology
            modules_to_pop = set(self._modules) - current_module_ids

            for module in modules_to_pop:
                self._modules_to_remove[module] = self._modules.pop(module)

        return self._modules
