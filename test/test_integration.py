import asyncio

import pytest
from aiohttp import ClientResponseError

from homepluscontrol import (
    homepluslight,
    homeplusplant,
    homeplusplug,
    homeplusremote,
    homeplusautomation,
)

# Integration tests


# Test error responses from the API
def test_error_responses(error_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    with pytest.raises(Exception) as exc_info:
        loop.run_until_complete(test_client.get_request("https://api.netatmo.com/api/homesdata"))

    assert exc_info.type is ClientResponseError
    assert exc_info.value.status == 400


# Happy path retrieval of plant data, plant topology and module status
# Including update of status of modules
def test_plant_data(mock_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(test_client.get_request("https://api.netatmo.com/api/homesdata"))
    response_body = loop.run_until_complete(resp.json())
    plant_info = response_body["body"]

    # Retrieve the first and only plant in the response
    p = plant_info["homes"][0]
    test_plant = homeplusplant.HomePlusPlant(p["id"], p, test_client)

    plant_str = "Home+ Home: name->My Home, id->123456789009876543210, country->ES"
    assert test_plant.__str__() == plant_str

    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_module_status())
    plugs = []
    lights = []
    remotes = []
    automations = []
    for mod in test_plant.modules.values():
        if isinstance(mod, homeplusplug.HomePlusPlug):
            plugs.append(mod)
        elif isinstance(mod, homepluslight.HomePlusLight):
            lights.append(mod)
        elif isinstance(mod, homeplusremote.HomePlusRemote):
            remotes.append(mod)
        elif isinstance(mod, homeplusautomation.HomePlusAutomation):
            automations.append(mod)

    assert len(test_plant.modules) == 12
    assert len(plugs) == 4
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2

    # Confirm status ON of the plugs
    for p in plugs:
        assert p.status == "on"

    # Confirm status OFF of the lights
    for lg in lights:
        assert lg.status == "off"

    # Confirm battery is full on remotes
    for r in remotes:
        assert r.battery == "full"

    # Turn off a plug: aa:87:65:43:21:fe:dc:ba
    test_plug = test_plant.modules["aa:87:65:43:21:fe:dc:ba"]
    loop.run_until_complete(test_plug.turn_off())
    assert test_plug.status == "off"

    # Turn on a light: aa:11:11:32:11:ae:df:11
    test_light = test_plant.modules["aa:11:11:32:11:ae:df:11"]
    loop.run_until_complete(test_light.turn_on())
    assert test_light.status == "on"


# Topology loses a couple of modules, so the number of modules before and after should reflect this
def test_reducing_plant(mock_reduced_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(test_client.get_request("https://api.netatmo.com/api/homesdata"))
    response_body = loop.run_until_complete(resp.json())
    plant_info = response_body["body"]

    # Retrieve the first and only plant in the response
    p = plant_info["homes"][0]
    test_plant = homeplusplant.HomePlusPlant(p["id"], p, test_client)

    plant_str = "Home+ Home: name->My Home, id->123456789009876543210, country->ES"
    assert test_plant.__str__() == plant_str

    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_module_status())
    plugs = []
    lights = []
    remotes = []
    automations = []
    for mod in test_plant.modules.values():
        if isinstance(mod, homeplusplug.HomePlusPlug):
            plugs.append(mod)
        elif isinstance(mod, homepluslight.HomePlusLight):
            lights.append(mod)
        elif isinstance(mod, homeplusremote.HomePlusRemote):
            remotes.append(mod)
        elif isinstance(mod, homeplusautomation.HomePlusAutomation):
            automations.append(mod)

    assert len(test_plant.modules) == 12
    assert len(plugs) == 4
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2

    # Now change the topology and assert that the updates are "seen" in the plant object
    loop.run_until_complete(test_plant.update_home_data_and_modules())
    plugs = []
    lights = []
    remotes = []
    automations = []
    for mod in test_plant.modules.values():
        if isinstance(mod, homeplusplug.HomePlusPlug):
            plugs.append(mod)
        elif isinstance(mod, homepluslight.HomePlusLight):
            lights.append(mod)
        elif isinstance(mod, homeplusremote.HomePlusRemote):
            remotes.append(mod)
        elif isinstance(mod, homeplusautomation.HomePlusAutomation):
            automations.append(mod)

    # Reduced topology has 4 modules fewer - one plug, one remote, one light and one automation have been removed
    assert len(test_plant.modules) == 8
    assert len(plugs) == 3
    assert len(lights) == 1
    assert len(remotes) == 2
    assert len(automations) == 1


# Topology remains the same, but we lose some of the modules' status
# The missing modules should change their reachability to False
def test_reducing_module_status(mock_reduced_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(test_client.get_request("https://api.netatmo.com/api/homesdata"))
    response_body = loop.run_until_complete(resp.json())
    plant_info = response_body["body"]

    # Retrieve the first and only plant in the response
    p = plant_info["homes"][0]
    test_plant = homeplusplant.HomePlusPlant(p["id"], p, test_client)

    plant_str = "Home+ Home: name->My Home, id->123456789009876543210, country->ES"
    assert test_plant.__str__() == plant_str

    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_module_status())
    plugs = []
    lights = []
    remotes = []
    automations = []
    for mod in test_plant.modules.values():
        if isinstance(mod, homeplusplug.HomePlusPlug):
            plugs.append(mod)
        elif isinstance(mod, homepluslight.HomePlusLight):
            lights.append(mod)
        elif isinstance(mod, homeplusremote.HomePlusRemote):
            remotes.append(mod)
        elif isinstance(mod, homeplusautomation.HomePlusAutomation):
            automations.append(mod)

    assert len(test_plant.modules) == 12
    assert len(plugs) == 4
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2

    missing_plug = test_plant.modules["aa:34:ab:f3:ff:4e:22:b1"]
    missing_remote = test_plant.modules["aa:45:21:aa:1b:fc:bd:da"]
    missing_automation = test_plant.modules["aa:88:99:43:18:1f:09:76"]
    assert missing_plug.reachable
    assert missing_remote.reachable
    assert missing_automation.reachable

    # Now change the topology and assert that the updates are "seen" in the plant object
    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_module_status())
    plugs = []
    lights = []
    remotes = []
    automations = []
    for mod in test_plant.modules.values():
        if isinstance(mod, homeplusplug.HomePlusPlug):
            plugs.append(mod)
        elif isinstance(mod, homepluslight.HomePlusLight):
            lights.append(mod)
        elif isinstance(mod, homeplusremote.HomePlusRemote):
            remotes.append(mod)
        elif isinstance(mod, homeplusautomation.HomePlusAutomation):
            automations.append(mod)

    # Reduced topology has 3 modules fewer - one plug, one remote and one automation have been removed
    # But we have not updated the topology in the plant object, only the module status has been refreshed
    # So number of modules should be the same...
    assert len(test_plant.modules) == 12
    assert len(plugs) == 4
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2

    # But we should see that the missing modules are now unreachable
    assert not missing_plug.reachable
    assert not missing_remote.reachable
    assert not missing_automation.reachable


# Topology gains a couple of modules, so the number of modules before and after should reflect this
def test_growing_plant(mock_growing_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(test_client.get_request("https://api.netatmo.com/api/homesdata"))
    response_body = loop.run_until_complete(resp.json())
    plant_info = response_body["body"]

    # Retrieve the first and only plant in the response
    p = plant_info["homes"][0]
    test_plant = homeplusplant.HomePlusPlant(p["id"], p, test_client)

    plant_str = "Home+ Home: name->My Home, id->123456789009876543210, country->ES"
    assert test_plant.__str__() == plant_str

    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_module_status())
    plugs = []
    lights = []
    remotes = []
    automations = []
    for mod in test_plant.modules.values():
        if isinstance(mod, homeplusplug.HomePlusPlug):
            plugs.append(mod)
        elif isinstance(mod, homepluslight.HomePlusLight):
            lights.append(mod)
        elif isinstance(mod, homeplusremote.HomePlusRemote):
            remotes.append(mod)
        elif isinstance(mod, homeplusautomation.HomePlusAutomation):
            automations.append(mod)

    assert len(test_plant.modules) == 8
    assert len(plugs) == 3
    assert len(lights) == 1
    assert len(remotes) == 2
    assert len(automations) == 1

    # Now change the topology and assert that the updates are "seen" in the plant object
    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_home_data_and_modules())
    plugs = []
    lights = []
    remotes = []
    automations = []
    for mod in test_plant.modules.values():
        if isinstance(mod, homeplusplug.HomePlusPlug):
            plugs.append(mod)
        elif isinstance(mod, homepluslight.HomePlusLight):
            lights.append(mod)
        elif isinstance(mod, homeplusremote.HomePlusRemote):
            remotes.append(mod)
        elif isinstance(mod, homeplusautomation.HomePlusAutomation):
            automations.append(mod)

    # Increased topology has 4 modules more - one plug, one remote, one light and one automation have been added
    assert len(test_plant.modules) == 12
    assert len(plugs) == 4
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2


# Topology gains a couple of modules, but they do not have module status
# The missing modules should change their reachability to False
def test_increasing_module_status(mock_growing_plant_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(test_client.get_request("https://api.netatmo.com/api/homesdata"))
    response_body = loop.run_until_complete(resp.json())
    plant_info = response_body["body"]

    # Retrieve the first and only plant in the response
    p = plant_info["homes"][0]
    test_plant = homeplusplant.HomePlusPlant(p["id"], p, test_client)

    plant_str = "Home+ Home: name->My Home, id->123456789009876543210, country->ES"
    assert test_plant.__str__() == plant_str

    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_module_status())
    plugs = []
    lights = []
    remotes = []
    automations = []
    for mod in test_plant.modules.values():
        if isinstance(mod, homeplusplug.HomePlusPlug):
            plugs.append(mod)
        elif isinstance(mod, homepluslight.HomePlusLight):
            lights.append(mod)
        elif isinstance(mod, homeplusremote.HomePlusRemote):
            remotes.append(mod)
        elif isinstance(mod, homeplusautomation.HomePlusAutomation):
            automations.append(mod)

    assert len(test_plant.modules) == 8
    assert len(plugs) == 3
    assert len(lights) == 1
    assert len(remotes) == 2
    assert len(automations) == 1

    new_plug = test_plant.modules.get("aa:34:ab:f3:ff:4e:22:b1", None)
    new_remote = test_plant.modules.get("aa:45:21:aa:1b:fc:bd:da", None)
    new_automation = test_plant.modules.get("aa:88:99:43:18:1f:09:76", None)
    assert new_plug is None
    assert new_remote is None
    assert new_automation is None

    # Now change the topology and assert that the updates are "seen" in the plant object
    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_home_data_and_modules())
    plugs = []
    lights = []
    remotes = []
    automations = []
    for mod in test_plant.modules.values():
        if isinstance(mod, homeplusplug.HomePlusPlug):
            plugs.append(mod)
        elif isinstance(mod, homepluslight.HomePlusLight):
            lights.append(mod)
        elif isinstance(mod, homeplusremote.HomePlusRemote):
            remotes.append(mod)
        elif isinstance(mod, homeplusautomation.HomePlusAutomation):
            automations.append(mod)

    # Increased topology has 3 modules more - one plug, one remote and one automation have been added.
    # We have only updated the topology and not the module status, so by default, the new modules should be unreachable
    # Number of modules grows...
    assert len(test_plant.modules) == 12
    assert len(plugs) == 4
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2

    # But we should see that the new modules are unreachable
    new_plug = test_plant.modules.get("aa:34:ab:f3:ff:4e:22:b1", None)
    new_remote = test_plant.modules.get("aa:45:21:aa:1b:fc:bd:da", None)
    new_automation = test_plant.modules.get("aa:88:99:43:18:1f:09:76", None)
    assert not new_plug.reachable
    assert not new_remote.reachable
    assert not new_automation.reachable

    # If we now update the module status, they become reachable (because they are defined as so in the test data)
    loop.run_until_complete(test_plant.update_module_status())
    assert new_plug.reachable
    assert new_remote.reachable
    assert new_automation.reachable


# Test a case where we get an HTTP error while updating the module status
def test_plant_partial_error(partial_error_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(test_client.get_request("https://api.netatmo.com/api/homesdata"))
    response_body = loop.run_until_complete(resp.json())
    plant_info = response_body["body"]

    # Retrieve the first and only plant in the response
    p = plant_info["homes"][0]
    test_plant = homeplusplant.HomePlusPlant(p["id"], p, test_client)

    plant_str = "Home+ Home: name->My Home, id->123456789009876543210, country->ES"
    assert test_plant.__str__() == plant_str

    # Now read the module status, but it fails with an HTTP error
    loop.run_until_complete(test_plant.update_module_status())
    plugs = []
    lights = []
    remotes = []
    automations = []
    for mod in test_plant.modules.values():
        if isinstance(mod, homeplusplug.HomePlusPlug):
            plugs.append(mod)
        elif isinstance(mod, homepluslight.HomePlusLight):
            lights.append(mod)
        elif isinstance(mod, homeplusremote.HomePlusRemote):
            remotes.append(mod)
        elif isinstance(mod, homeplusautomation.HomePlusAutomation):
            automations.append(mod)

    # Modules are there, but they are all unreachable
    assert len(test_plant.modules) == 12
    assert len(plugs) == 4
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2

    for mod in test_plant.modules.values():
        assert not mod.reachable

    # Now we re-read home data and module status to fix the situation
    loop.run_until_complete(test_plant.update_home_data_and_modules())
    plugs = []
    lights = []
    remotes = []
    automations = []
    for mod in test_plant.modules.values():
        if isinstance(mod, homeplusplug.HomePlusPlug):
            plugs.append(mod)
        elif isinstance(mod, homepluslight.HomePlusLight):
            lights.append(mod)
        elif isinstance(mod, homeplusremote.HomePlusRemote):
            remotes.append(mod)
        elif isinstance(mod, homeplusautomation.HomePlusAutomation):
            automations.append(mod)

    # Modules are still there
    assert len(test_plant.modules) == 12
    assert len(plugs) == 4
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2

    # And are now reachable
    for mod in test_plant.modules.values():
        assert mod.reachable
