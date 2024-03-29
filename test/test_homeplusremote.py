from homepluscontrol import (
    homeplusinteractivemodule,
    homeplusmodule,
    homeplusremote,
)


# Remote Module Tests
def test_remote_module_str(test_remote):
    module_str = "Home+ Remote: device->Remote, name->Remote Module 1, id->module_id_4, reachable->False, battery->, battery_level->, bridge->00:11:22:33:44:55"
    assert test_remote.__str__() == module_str


def test_remote_read_status(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_remote = mock_plant.modules["aa:23:45:00:00:ab:cd:fe"]

    assert isinstance(mock_remote, homeplusmodule.HomePlusModule)
    assert not isinstance(mock_remote, homeplusinteractivemodule.HomePlusInteractiveModule)
    assert isinstance(mock_remote, homeplusremote.HomePlusRemote)
    assert mock_remote.device == "remote"
    assert mock_remote.name == "General Command"
    assert mock_remote.hw_type == "NLT"
    assert mock_remote.battery == "full"
    assert mock_remote.battery_level == 2600
    assert mock_remote.fw == 42


def test_remote_update_status(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_remote = mock_plant.modules["aa:23:45:00:00:ab:cd:fe"]

    status_result = loop.run_until_complete(mock_remote.get_status_update())
    assert isinstance(mock_remote, homeplusmodule.HomePlusModule)
    assert not isinstance(mock_remote, homeplusinteractivemodule.HomePlusInteractiveModule)
    assert isinstance(mock_remote, homeplusremote.HomePlusRemote)
    assert status_result["reachable"]
    assert status_result["firmware_revision"] is not None
    assert status_result["battery_state"] == "full"
    assert status_result["battery_level"] == 2600

    assert mock_remote.battery == "full"
    assert mock_remote.fw == 42
    assert mock_remote.battery_level == 2600
    assert mock_remote.reachable

    assert mock_remote.device == "remote"
    assert mock_remote.name == "General Command"
    assert mock_remote.hw_type == "NLT"
