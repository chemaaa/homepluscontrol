import asyncio

from homepluscontrol import (
    homeplusapi,
)

# Define intervals so that API is always called
TEST_UPDATE_INTERVAL = -1

# Implement a dummy class for testing
class MockHomePlusControlAPI(homeplusapi.HomePlusControlAPI):
    def __init__(self, oauth_client, update_intervals):
        super().__init__(oauth_client, update_intervals)

    async def async_get_access_token(self):
        return self.oauth_client.token


def test_handle_plant_data(mock_plant_aioresponse, test_client):
    loop = asyncio.get_event_loop()
    test_api = MockHomePlusControlAPI(test_client, TEST_UPDATE_INTERVAL)
    loop.run_until_complete(test_api.async_handle_home_data())

    # Run once - one plant
    assert len(test_api._homes) == 1
    # Run again - two plants
    loop.run_until_complete(test_api.async_handle_home_data())
    assert len(test_api._homes) == 2
    # Run thrice - back to one plant
    loop.run_until_complete(test_api.async_handle_home_data())
    assert len(test_api._homes) == 1


def test_handle_module_status(mock_aioresponse, test_client):
    loop = asyncio.get_event_loop()
    test_api = MockHomePlusControlAPI(test_client, TEST_UPDATE_INTERVAL)

    loop.run_until_complete(test_api.async_handle_home_data())
    loop.run_until_complete(test_api.async_get_modules())
    assert len(test_api._homes) == 1
    assert len(test_api._modules) == 12
    # Light is in the API modules
    assert "aa:77:11:43:18:de:df:12" in test_api._modules
    # Remote is in the API modules
    assert "aa:34:97:56:13:cc:bb:aa" in test_api._modules
    # Automation is in the API modules
    assert "aa:34:56:78:90:00:0c:dd" in test_api._modules
