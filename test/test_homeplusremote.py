from homepluscontrol import (
    homeplusinteractivemodule,
    homeplusmodule,
    homeplusremote,
)


# Remote Module Tests
def test_remote_module_url(test_remote):
    assert (
        test_remote.statusUrl
        == "https://api.developer.legrand.com/hc/api/v1.0/remote/remote/addressLocation/plants/mock_plant_1/modules/parameter/id/value/module_id_4"
    )


def test_remote_module_str(test_remote):
    module_str = "Home+ Remote: device->Remote, name->Remote Module 1, id->module_id_4, reachable->False, battery->"
    assert test_remote.__str__() == module_str


def test_remote_read_status(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_remote = mock_plant.modules["000000012345678abcdef"]

    assert isinstance(mock_remote, homeplusmodule.HomePlusModule)
    assert not isinstance(
        mock_remote, homeplusinteractivemodule.HomePlusInteractiveModule
    )
    assert isinstance(mock_remote, homeplusremote.HomePlusRemote)
    assert mock_remote.device == "remote"
    assert mock_remote.name == "General Command"
    assert mock_remote.hw_type == "NLT"
    assert mock_remote.battery == "full"
    assert mock_remote.fw == 36


def test_remote_update_status(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_remote = mock_plant.modules["000000012345678abcdef"]

    status_result = loop.run_until_complete(mock_remote.get_status_update())
    assert isinstance(mock_remote, homeplusmodule.HomePlusModule)
    assert not isinstance(
        mock_remote, homeplusinteractivemodule.HomePlusInteractiveModule
    )
    assert isinstance(mock_remote, homeplusremote.HomePlusRemote)
    assert not status_result["reachable"]
    assert status_result["fw"] is not None
    assert status_result["battery"] == "full"

    assert mock_remote.battery == "full"
    assert mock_remote.fw == 36
    assert not mock_remote.reachable

    assert mock_remote.device == "remote"
    assert mock_remote.name == "General Command"
    assert mock_remote.hw_type == "NLT"
