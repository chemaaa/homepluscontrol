from homepluscontrol import (
    homeplusinteractivemodule,
    homeplusmodule,
    homeplusplug,
)


# Plug Module Tests
def test_plug_module_url(test_plug):
    assert (
        test_plug.statusUrl
        == "https://api.developer.legrand.com/hc/api/v1.0/plug/energy/addressLocation/plants/mock_plant_1/modules/parameter/id/value/module_id_2"
    )


def test_plug_module_str(test_plug):
    module_str = "Home+ Plug: device->Plug, name->Plug Module 1, id->module_id_2, reachable->False, status->"
    assert test_plug.__str__() == module_str


def test_plug_read_status(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_plug = mock_plant.modules["0000000587654321fedcba"]

    assert isinstance(mock_plug, homeplusmodule.HomePlusModule)
    assert isinstance(mock_plug, homeplusinteractivemodule.HomePlusInteractiveModule)
    assert isinstance(mock_plug, homeplusplug.HomePlusPlug)
    assert mock_plug.device == "plug"
    assert mock_plug.name == "Dining Room Wall Outlet"
    assert mock_plug.hw_type == "NLP"
    assert mock_plug.status == "on"
    assert mock_plug.power == 0
    assert mock_plug.reachable
    assert mock_plug.fw == 42


def test_plug_update_status(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_plug = mock_plant.modules["0000000587654321fedcba"]

    status_result = loop.run_until_complete(mock_plug.get_status_update())
    assert isinstance(mock_plug, homeplusmodule.HomePlusModule)
    assert isinstance(mock_plug, homeplusinteractivemodule.HomePlusInteractiveModule)
    assert isinstance(mock_plug, homeplusplug.HomePlusPlug)
    assert status_result["reachable"]
    assert status_result["fw"] is not None
    assert status_result["status"] == "on"

    assert mock_plug.status == "on"
    assert mock_plug.power == 1999
    assert mock_plug.reachable
    assert mock_plug.fw == 42

    assert mock_plug.device == "plug"
    assert mock_plug.name == "Dining Room Wall Outlet"
    assert mock_plug.hw_type == "NLP"


def test_plug_turn_on(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_plug = mock_plant.modules["0000000587654321fedcba"]

    loop.run_until_complete(mock_plug.turn_on())
    assert mock_plug.status == "on"


def test_plug_turn_off(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_plug = mock_plant.modules["0000000587654321fedcba"]

    loop.run_until_complete(mock_plug.turn_off())
    assert mock_plug.status == "off"


def test_plug_toggle(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_plug = mock_plant.modules["0000000587654321fedcba"]

    # Fixture light is on to start with
    loop.run_until_complete(mock_plug.toggle_status())
    assert mock_plug.status == "off"
