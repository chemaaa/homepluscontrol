import asyncio

from homepluscontrol import (
    homeplusapi,
)

from homepluscontrol.homeplusapi import (
    CONF_PLANT_UPDATE_INTERVAL,
    CONF_PLANT_TOPOLOGY_UPDATE_INTERVAL,
    CONF_MODULE_STATUS_UPDATE_INTERVAL,
)

# Define intervals so that API is always called
TEST_UPDATE_INTERVALS = {
    CONF_PLANT_UPDATE_INTERVAL: -1,
    CONF_PLANT_TOPOLOGY_UPDATE_INTERVAL: -1,
    CONF_MODULE_STATUS_UPDATE_INTERVAL: -1,
}


# Implement a dummy class for testing
class MockHomePlusControlAPI(homeplusapi.HomePlusControlAPI):

    def __init__(self, subscription_key, oauth_client, update_intervals):
        super().__init__(subscription_key, oauth_client, update_intervals)

    async def async_get_access_token(self):
        pass


def test_handle_plant_data(mock_plant_aioresponse, test_client):
    loop = asyncio.get_event_loop()
    test_api = MockHomePlusControlAPI("subscription_key", test_client, TEST_UPDATE_INTERVALS)
    loop.run_until_complete(test_api.async_handle_plant_data())

    # Run once - one plant
    assert len(test_api._plants) == 1
    # Run again - two plants
    loop.run_until_complete(test_api.async_handle_plant_data())
    assert len(test_api._plants) == 2
    # Run thrice - back to one plant
    loop.run_until_complete(test_api.async_handle_plant_data())
    assert len(test_api._plants) == 1


def test_handle_module_status(mock_aioresponse, test_client):
    loop = asyncio.get_event_loop()
    test_api = MockHomePlusControlAPI("subscription_key", test_client, TEST_UPDATE_INTERVALS)

    loop.run_until_complete(test_api.async_handle_plant_data())
    assert len(test_api._plants) == 1

    loop.run_until_complete(test_api.async_handle_module_status())
    assert len(test_api._modules) == 5
    # Light is in the API modules
    assert '0000000987654321fedcba' in test_api._modules
    # But remote is not in the API modules
    assert '000000012345678abcdef' not in test_api._modules
