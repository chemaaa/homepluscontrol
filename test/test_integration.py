from aioresponses import aioresponses
import asyncio
from aiohttp import ClientResponseError
from homepluscontrol import authentication, homeplusplant, homeplusmodule, homeplusplug, homepluslight, homeplusremote
import pytest
import time

# Integration tests

def test_error_responses(error_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    with pytest.raises(Exception) as exc_info:
        resp = loop.run_until_complete(test_client.get_request('https://api.developer.legrand.com/hc/api/v1.0/plants'))
    
    assert exc_info.type is ClientResponseError
    assert exc_info.value.status == 400

def test_plant_data(mock_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(test_client.get_request('https://api.developer.legrand.com/hc/api/v1.0/plants'))
    plant_info = loop.run_until_complete(resp.json())

    # Retrieve the first and only plant in the response
    p = plant_info['plants'][0]
    test_plant = homeplusplant.HomePlusPlant(p['id'], p['name'], p['country'], test_client)

    plant_str = "Home+ Plant: name->My Home, id->123456789009876543210, country->ES"
    assert test_plant.__str__() == plant_str

    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_topology_and_modules())
    plugs = []
    lights = []
    remotes = []
    for mod in test_plant.modules.values():
        if isinstance(mod, homeplusplug.HomePlusPlug):
            plugs.append(mod)
        elif isinstance(mod, homepluslight.HomePlusLight):
            lights.append(mod)
        elif isinstance(mod, homeplusremote.HomePlusRemote):
            remotes.append(mod)

    assert len(test_plant.modules) == 8
    assert len(plugs) == 3
    assert len(lights) == 2
    assert len(remotes) == 3

    # Confirm status ON of the plugs
    for p in plugs:
        assert p.status == 'on'

    # Confirm status OFF of the lights
    for lg in lights:
        assert lg.status == 'off'

    # Confirm battery is full on remotes
    for r in remotes:
        assert r.battery == "full"

    # Turn off a plug: 0000000587654321fedcba
    test_plug = test_plant.modules["0000000587654321fedcba"]
    loop.run_until_complete(test_plug.turn_off())
    assert test_plug.status == "off"

    # Turn on a light: 0000000787654321fedcba
    test_light = test_plant.modules["0000000787654321fedcba"]
    loop.run_until_complete(test_light.turn_on())
    assert test_light.status == "on"




    