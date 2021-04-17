from homepluscontrol import (
    homeplusinteractivemodule,
    homepluslight,
    homeplusmodule,
)


# Light Module Tests
def test_light_module_url(test_light):
    assert (
        test_light.statusUrl
        == "https://api.developer.legrand.com/hc/api/v1.0/light/lighting/addressLocation/plants/mock_plant_1/modules/parameter/id/value/module_id_3"
    )


def test_light_module_str(test_light):
    module_str = "Home+ Light: device->Light, name->Light Module 1, id->module_id_3, reachable->False, status->"
    assert test_light.__str__() == module_str


def test_light_read_status(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_light = mock_plant.modules["0000000787654321fedcba"]

    assert isinstance(mock_light, homeplusmodule.HomePlusModule)
    assert isinstance(mock_light, homeplusinteractivemodule.HomePlusInteractiveModule)
    assert isinstance(mock_light, homepluslight.HomePlusLight)
    assert mock_light.device == "light"
    assert mock_light.name == "Living Room Ceiling Light"
    assert mock_light.hw_type == "NLF"
    assert mock_light.status == "off"
    assert mock_light.power == 0
    assert mock_light.reachable
    assert mock_light.fw == 46


def test_light_update_status(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_light = mock_plant.modules["0000000787654321fedcba"]

    status_result = loop.run_until_complete(mock_light.get_status_update())
    assert isinstance(mock_light, homeplusmodule.HomePlusModule)
    assert isinstance(mock_light, homeplusinteractivemodule.HomePlusInteractiveModule)
    assert isinstance(mock_light, homepluslight.HomePlusLight)
    assert status_result["reachable"]
    assert status_result["fw"] is not None
    assert status_result["status"] == "off"

    assert mock_light.status == "off"
    assert mock_light.power == 0
    assert mock_light.reachable
    assert mock_light.fw == 46

    assert mock_light.device == "light"
    assert mock_light.name == "Living Room Ceiling Light"
    assert mock_light.hw_type == "NLF"


def test_light_turn_on(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_light = mock_plant.modules["0000000787654321fedcba"]

    loop.run_until_complete(mock_light.turn_on())
    assert mock_light.status == "on"


def test_light_turn_off(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_light = mock_plant.modules["0000000787654321fedcba"]

    loop.run_until_complete(mock_light.turn_off())
    assert mock_light.status == "off"


def test_light_toggle(async_mock_plant):
    mock_plant, loop = async_mock_plant
    mock_light = mock_plant.modules["0000000787654321fedcba"]

    # Fixture light is off to start with
    loop.run_until_complete(mock_light.toggle_status())
    assert mock_light.status == "on"
