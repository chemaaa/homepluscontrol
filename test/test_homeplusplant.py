import asyncio

from homepluscontrol import (
    homeplusplant,
    homeplusplug,
)


# Plant Tests
def test_plant_str(test_plant):
    plant_str = "Home+ Home: name->Mock Plant, id->mock_plant_1, country->The World"
    assert test_plant.__str__() == plant_str


def test_topology_and_module_update(async_mock_plant):
    mock_plant = async_mock_plant[0]
    assert isinstance(mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"], homeplusplug.HomePlusPlug)
    assert mock_plant.modules["aa:11:11:32:11:ae:df:11"].name == "Living Room Ceiling Light"
    assert mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"].fw == 68
    assert mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"].status == "on"
    assert mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"].reachable
    assert mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"].power == 2


def test_topology_update(mock_aioresponse, test_client):
    loop = asyncio.get_event_loop()
    mock_plant = homeplusplant.HomePlusPlant("123456789009876543210", "My Home", "ES", test_client)
    loop.run_until_complete(mock_plant.update_topology())
    # The plug module has been created
    assert isinstance(mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"], homeplusplug.HomePlusPlug)
    assert mock_plant.modules["aa:11:11:32:11:ae:df:11"].name == "Living Room Ceiling Light"
    # But it should not have the status
    assert mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"].fw == ""
    assert mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"].status == ""
    assert not mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"].reachable


def test_module_status_update(mock_aioresponse, test_client):
    loop = asyncio.get_event_loop()
    mock_plant = homeplusplant.HomePlusPlant("123456789009876543210", "My Home", "ES", test_client)
    loop.run_until_complete(mock_plant.update_module_status())
    # The plug module has not been created because the topology is empty!
    assert len(mock_plant.modules) == 0


def test_topology_and_module_separate_update(mock_aioresponse, test_client):
    loop = asyncio.get_event_loop()
    mock_plant = homeplusplant.HomePlusPlant("123456789009876543210", "My Home", "ES", test_client)
    loop.run_until_complete(mock_plant.update_module_status())
    # The plug module has not been created because the topology is empty!
    assert len(mock_plant.modules) == 0
    # Now we fetch the topology
    loop.run_until_complete(mock_plant.update_topology())
    # The plug module has been created now
    assert isinstance(mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"], homeplusplug.HomePlusPlug)
    assert mock_plant.modules["aa:11:11:32:11:ae:df:11"].name == "Living Room Ceiling Light"
    # But it should not have the status
    assert mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"].fw == ""
    assert mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"].status == ""
    assert not mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"].reachable
    # So we update the module status again and the status should be there
    loop.run_until_complete(mock_plant.update_module_status())
    assert mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"].fw == 68
    assert mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"].status == "on"
    assert mock_plant.modules["aa:34:ab:f3:ff:4e:22:b1"].reachable
