import asyncio

from homepluscontrol import (
    homeplusplant,
    homeplusplug,
)


# Plant Tests
def test_plant_str(test_plant):
    plant_str = "Home+ Plant: name->Mock Plant, id->mock_plant_1, country->The World"
    assert test_plant.__str__() == plant_str


def test_topology_and_module_update(async_mock_plant):
    mock_plant = async_mock_plant[0]
    assert isinstance(
        mock_plant.modules["0000000987654321fedcba"], homeplusplug.HomePlusPlug
    )
    assert (
        mock_plant.modules["0000000787654321fedcba"].name == "Living Room Ceiling Light"
    )
    assert mock_plant.modules["0000000987654321fedcba"].fw == 42
    assert mock_plant.modules["0000000987654321fedcba"].status == "on"
    assert mock_plant.modules["0000000987654321fedcba"].reachable
    assert mock_plant.modules["0000000987654321fedcba"].power == 89


def test_topology_update(mock_aioresponse, test_client):
    loop = asyncio.get_event_loop()
    mock_plant = homeplusplant.HomePlusPlant(
        "123456789009876543210", "My Home", "ES", test_client
    )
    loop.run_until_complete(mock_plant.update_topology())
    # The plug module has been created
    assert isinstance(
        mock_plant.modules["0000000987654321fedcba"], homeplusplug.HomePlusPlug
    )
    assert (
        mock_plant.modules["0000000787654321fedcba"].name == "Living Room Ceiling Light"
    )
    # But it should not have the status
    assert mock_plant.modules["0000000987654321fedcba"].fw == ""
    assert mock_plant.modules["0000000987654321fedcba"].status == ""
    assert not mock_plant.modules["0000000987654321fedcba"].reachable


def test_module_status_update(mock_aioresponse, test_client):
    loop = asyncio.get_event_loop()
    mock_plant = homeplusplant.HomePlusPlant(
        "123456789009876543210", "My Home", "ES", test_client
    )
    loop.run_until_complete(mock_plant.update_module_status())
    # The plug module has not been created because the topology is empty!
    assert len(mock_plant.modules) == 0


def test_topology_and_module_separate_update(mock_aioresponse, test_client):
    loop = asyncio.get_event_loop()
    mock_plant = homeplusplant.HomePlusPlant(
        "123456789009876543210", "My Home", "ES", test_client
    )
    loop.run_until_complete(mock_plant.update_module_status())
    # The plug module has not been created because the topology is empty!
    assert len(mock_plant.modules) == 0
    # Now we fetch the topology
    loop.run_until_complete(mock_plant.update_topology())
    # The plug module has been created now
    assert isinstance(
        mock_plant.modules["0000000987654321fedcba"], homeplusplug.HomePlusPlug
    )
    assert (
        mock_plant.modules["0000000787654321fedcba"].name == "Living Room Ceiling Light"
    )
    # But it should not have the status
    assert mock_plant.modules["0000000987654321fedcba"].fw == ""
    assert mock_plant.modules["0000000987654321fedcba"].status == ""
    assert not mock_plant.modules["0000000987654321fedcba"].reachable
    # So we update the module status again and the status should be there
    loop.run_until_complete(mock_plant.update_module_status())
    assert mock_plant.modules["0000000987654321fedcba"].fw == 42
    assert mock_plant.modules["0000000987654321fedcba"].status == "on"
    assert mock_plant.modules["0000000987654321fedcba"].reachable
