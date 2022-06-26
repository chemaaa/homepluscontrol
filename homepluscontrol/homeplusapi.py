import aiohttp
import logging

import time

from .authentication import AbstractHomePlusOAuth2Async
from .homeplusconst import HOMES_DATA_URL, HOMES_STATUS_URL
from .homeplusplant import HomePlusPlant

# The Netatmo Connect Home+ Control API has increased number of request quotas when compared to
# the Legrand platform. At the time of writing, the quota is 2000 calls per hour or 200 requests every 10 secs
DEFAULT_UPDATE_INTERVAL = 10  # 10 seconds


class HomePlusControlApiError(Exception):
    """General HomePlusControlApi error occurred."""


class HomePlusControlAPI(AbstractHomePlusOAuth2Async):
    """Presents a unique API to the Home+ Control platform.

    This class is an implementation of the base class AbstractHomePlusOAuth2Async and is intended for the integration
    into Home Assistant.

    This class presents a unified view of the interactive modules that are available in the Home+ Control platform
    through the method `async_get_modules()` and it handles the refresh of the different elements of the home topology and
    module status.

    This class is still in an abstract form because it does not implement the method `async_get_access_token()`. That
    is provided through the Home Assistant integration.

    Attributes:
        oauth_client (:obj:`ClientSession`): aiohttp ClientSession object that handles HTTP async requests
        _homes (dict): Dictionary containing the information of all homes.
        _modules (dict): Dictionary containing the information of all modules in the homes.
        _modules_to_remove (dict): Dictionary containing the information of modules that are no longer in the homes' topology.
        _refresh_interval (int): Configured update interval for home and module status information (in seconds).
    """

    def __init__(self, oauth_client=None, update_interval=DEFAULT_UPDATE_INTERVAL):
        """HomePlusControlAPI Constructor

        Args:
            oauth_client (:obj:`ClientSession`): aiohttp ClientSession object that handles HTTP async requests
            update_interval (int): Optional refresh interval for the home data in seconds
        """
        super().__init__(
            oauth_client=oauth_client,
        )
        self._homes = {}
        self._modules = {}
        self._modules_to_remove = {}
        self._last_check = time.monotonic()
        # Set the update interval
        self._refresh_interval = update_interval

    @property
    def logger(self):
        """Return logger of the API."""
        return logging.getLogger(__name__)

    async def async_get_modules(self):
        """Retrieve the module information.

        Returns:
            dict: Dictionary of modules across all of the homes keyed by the unique platform identifier.
        """
        await self.async_handle_home_data()
        return self._update_modules()

    async def async_handle_home_data(self):
        """Recover the home data for this particular user.

        This will populate the "private" array of homes of this object and will return it.
        It is expected that in most cases, there will only be one home.

        Returns:
            dict: Dictionary of homes for this user - Keyed by the home ID. Can be empty if no
                  homes are retrieved.
        """
        # Attempt to recover the home information from the cache.
        # If it is not there, then we request it from the API and add it.
        # We also refresh from the API if the time has expired.
        if not self._homes or self._should_check():
            try:
                result = await self.get_request(HOMES_DATA_URL)  # Call the API
                response_body = await result.json()
                homes_info = response_body["body"]
            except aiohttp.ClientError as err:
                raise HomePlusControlApiError("Error retrieving homes information") from err

            # If all goes well, we update the last check time
            self._last_check = time.monotonic()
            self.logger.debug("Obtained homes information from API: %s", homes_info)
        else:
            self.logger.debug(
                "Not refreshing data just yet. Obtained homes information from cached info: %s",
                self._homes,
            )
            return self._homes

        # Populate the dictionary of homes
        current_home_id = []
        for home in homes_info["homes"]:
            print(home)
            current_home_id.append(home["id"])
            if home["id"] in self._homes:
                self.logger.debug(
                    "Home with id %s is already cached. Only updating the existing data.",
                    home["id"],
                )
                cur_home = self._homes.get(home["id"])
                # We will update the home info just in case and ensure it has an Api object
                cur_home.name = home["name"]
                cur_home.country = home["country"]
                if cur_home.oauth_client is None:
                    cur_home.oauth_client = self
            else:
                self.logger.debug("New home with id %s detected.", home["id"])
                self._homes[home["id"]] = HomePlusPlant(home["id"], home, self)

            # Update the module status information in the home - this makes an API call
            await self._homes[home["id"]].update_home_data_and_modules(input_home_data=home)

        # Discard homes that may have disappeared
        homes_to_pop = set(self._homes) - set(current_home_id)

        for home_id in homes_to_pop:
            self.logger.debug("Home with id %s is no longer present, so remove from cache.", home_id)
            self._homes.pop(home_id, None)

        return self._homes

    def _should_check(self):
        """Return True if the current monotonic time is > the last check time plus a fixed period.

        Args:
            check_type (str): Type that identifies the timer that has to be used
            period (float): Number of fractional seconds to add to the last check time
        """
        current_time = time.monotonic()
        if current_time > self._last_check + self._refresh_interval:
            self.logger.debug(
                "Last check time (%.2f) exceeded by more than %.2f sec - monotonic time %.2f",
                self._last_check,
                self._refresh_interval,
                current_time,
            )
            return True
        return False

    def _update_modules(self):
        """Update the modules based on the collected information in the home object.

        Returns:
            dict: Dictionary of modules across all of the homes.
        """
        for home in self._homes.values():
            current_module_ids = set()
            for module in list(home.modules.values()):
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
