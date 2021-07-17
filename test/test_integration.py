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
        loop.run_until_complete(
            test_client.get_request(
                "https://api.developer.legrand.com/hc/api/v1.0/plants/"
            )
        )

    assert exc_info.type is ClientResponseError
    assert exc_info.value.status == 400


# Happy path retrieval of plant data, plant topology and module status
# Including update of status of modules
def test_plant_data(mock_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(
        test_client.get_request(
            "https://api.developer.legrand.com/hc/api/v1.0/plants/"
        )
    )
    plant_info = loop.run_until_complete(resp.json())

    # Retrieve the first and only plant in the response
    p = plant_info["plants"][0]
    test_plant = homeplusplant.HomePlusPlant(
        p["id"], p["name"], p["country"], test_client
    )

    plant_str = (
        "Home+ Plant: name->My Home, id->123456789009876543210, country->ES"
    )
    assert test_plant.__str__() == plant_str

    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_topology_and_modules())
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

    assert len(test_plant.modules) == 10
    assert len(plugs) == 3
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

    # Turn off a plug: 0000000587654321fedcba
    test_plug = test_plant.modules["0000000587654321fedcba"]
    loop.run_until_complete(test_plug.turn_off())
    assert test_plug.status == "off"

    # Turn on a light: 0000000787654321fedcba
    test_light = test_plant.modules["0000000787654321fedcba"]
    loop.run_until_complete(test_light.turn_on())
    assert test_light.status == "on"


# Topology loses a couple of modules, so the number of modules before and after should reflect this
def test_reducing_plant(mock_reduced_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(
        test_client.get_request(
            "https://api.developer.legrand.com/hc/api/v1.0/plants/"
        )
    )
    plant_info = loop.run_until_complete(resp.json())

    # Retrieve the first and only plant in the response
    p = plant_info["plants"][0]
    test_plant = homeplusplant.HomePlusPlant(
        p["id"], p["name"], p["country"], test_client
    )

    plant_str = (
        "Home+ Plant: name->My Home, id->123456789009876543210, country->ES"
    )
    assert test_plant.__str__() == plant_str

    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_topology_and_modules())
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

    assert len(test_plant.modules) == 10
    assert len(plugs) == 3
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2

    # Now change the topology and assert that the updates are "seen" in the plant object
    resp = loop.run_until_complete(
        test_client.get_request(
            "https://api.developer.legrand.com/hc/api/v1.0/plants/"
        )
    )
    plant_info = loop.run_until_complete(resp.json())

    # Retrieve the first and only plant in the response
    p = plant_info["plants"][0]
    test_plant = homeplusplant.HomePlusPlant(
        p["id"], p["name"], p["country"], test_client
    )

    plant_str = (
        "Home+ Plant: name->My Home, id->123456789009876543210, country->ES"
    )
    assert test_plant.__str__() == plant_str
    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_topology_and_modules())
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
    assert len(test_plant.modules) == 7
    assert len(plugs) == 2
    assert len(lights) == 2
    assert len(remotes) == 2
    assert len(automations) == 1


# Topology loses a couple of modules, but we only refresh the module status
# The missing modules should change their reachability to False
def test_reducing_module_status(mock_reduced_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(
        test_client.get_request(
            "https://api.developer.legrand.com/hc/api/v1.0/plants/"
        )
    )
    plant_info = loop.run_until_complete(resp.json())

    # Retrieve the first and only plant in the response
    p = plant_info["plants"][0]
    test_plant = homeplusplant.HomePlusPlant(
        p["id"], p["name"], p["country"], test_client
    )

    plant_str = (
        "Home+ Plant: name->My Home, id->123456789009876543210, country->ES"
    )
    assert test_plant.__str__() == plant_str

    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_topology_and_modules())
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

    assert len(test_plant.modules) == 10
    assert len(plugs) == 3
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2

    missing_plug = test_plant.modules["0000000987654321fedcba"]
    missing_remote = test_plant.modules["000000032345678abcdef"]
    missing_automation = test_plant.modules["00001234567890000xxxxxxx"]
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
    assert len(test_plant.modules) == 10
    assert len(plugs) == 3
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

    resp = loop.run_until_complete(
        test_client.get_request(
            "https://api.developer.legrand.com/hc/api/v1.0/plants/"
        )
    )
    plant_info = loop.run_until_complete(resp.json())

    # Retrieve the first and only plant in the response
    p = plant_info["plants"][0]
    test_plant = homeplusplant.HomePlusPlant(
        p["id"], p["name"], p["country"], test_client
    )

    plant_str = (
        "Home+ Plant: name->My Home, id->123456789009876543210, country->ES"
    )
    assert test_plant.__str__() == plant_str

    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_topology_and_modules())
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

    assert len(test_plant.modules) == 7
    assert len(plugs) == 2
    assert len(lights) == 2
    assert len(remotes) == 2
    assert len(automations) == 1

    # Now change the topology and assert that the updates are "seen" in the plant object
    resp = loop.run_until_complete(
        test_client.get_request(
            "https://api.developer.legrand.com/hc/api/v1.0/plants/"
        )
    )
    plant_info = loop.run_until_complete(resp.json())

    # Retrieve the first and only plant in the response
    p = plant_info["plants"][0]
    test_plant = homeplusplant.HomePlusPlant(
        p["id"], p["name"], p["country"], test_client
    )

    plant_str = (
        "Home+ Plant: name->My Home, id->123456789009876543210, country->ES"
    )
    assert test_plant.__str__() == plant_str
    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_topology_and_modules())
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

    # Increased topology has 3 modules more - one plug, one remote and one automation have been added
    assert len(test_plant.modules) == 10
    assert len(plugs) == 3
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2


# Topology gains a couple of modules, but we only refresh the module status
# The missing modules should change their reachability to False
def test_increasing_module_status(mock_growing_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(
        test_client.get_request(
            "https://api.developer.legrand.com/hc/api/v1.0/plants/"
        )
    )
    plant_info = loop.run_until_complete(resp.json())

    # Retrieve the first and only plant in the response
    p = plant_info["plants"][0]
    test_plant = homeplusplant.HomePlusPlant(
        p["id"], p["name"], p["country"], test_client
    )

    plant_str = (
        "Home+ Plant: name->My Home, id->123456789009876543210, country->ES"
    )
    assert test_plant.__str__() == plant_str

    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_topology_and_modules())
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

    assert len(test_plant.modules) == 7
    assert len(plugs) == 2
    assert len(lights) == 2
    assert len(remotes) == 2
    assert len(automations) == 1

    new_plug = test_plant.modules.get("0000000987654321fedcba", None)
    new_remote = test_plant.modules.get("000000032345678abcdef", None)
    new_automation = test_plant.modules.get("00001234567890000xxxxxxx", None)
    assert new_plug is None
    assert new_remote is None
    assert new_automation is None

    # Now change the topology and assert that the updates are "seen" in the plant object
    # Read the modules into arrays
    loop.run_until_complete(test_plant.update_topology())
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
    assert len(test_plant.modules) == 10
    assert len(plugs) == 3
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2

    # But we should see that the new modules are unreachable
    new_plug = test_plant.modules.get("0000000987654321fedcba", None)
    new_remote = test_plant.modules.get("000000032345678abcdef", None)
    new_automation = test_plant.modules.get("00001234567890000xxxxxxx", None)
    assert not new_plug.reachable
    assert not new_remote.reachable
    assert not new_automation.reachable

    # If we now update the module status, they become reachable (because they are defined as so in the test data)
    loop.run_until_complete(test_plant.update_module_status())
    assert new_plug.reachable
    assert new_remote.reachable
    assert new_automation.reachable


# Test a case where we update module status before topology
def test_plant_data_ordering(mock_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(
        test_client.get_request(
            "https://api.developer.legrand.com/hc/api/v1.0/plants/"
        )
    )
    plant_info = loop.run_until_complete(resp.json())

    # Retrieve the first and only plant in the response
    p = plant_info["plants"][0]
    test_plant = homeplusplant.HomePlusPlant(
        p["id"], p["name"], p["country"], test_client
    )

    plant_str = (
        "Home+ Plant: name->My Home, id->123456789009876543210, country->ES"
    )
    assert test_plant.__str__() == plant_str

    # Read the modules status, but we have no topology!!
    loop.run_until_complete(test_plant.update_module_status())
    assert len(test_plant.modules) == 0

    # Now read the topology
    loop.run_until_complete(test_plant.update_topology())
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
    assert len(test_plant.modules) == 10
    assert len(plugs) == 3
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2

    for mod in test_plant.modules.values():
        assert not mod.reachable

    # So we read the status to fix the situation
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

    # Modules are still there
    assert len(test_plant.modules) == 10
    assert len(plugs) == 3
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2

    # And are reachable (or whatever their test data says - 000000012345678abcdef is unreachable in the test data)
    for mod in test_plant.modules.values():
        if mod.id == "000000012345678abcdef":
            assert not mod.reachable
        else:
            assert mod.reachable


# Test a case where we get an HTTP error while updating the module status
def test_plant_partial_error(partial_error_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(
        test_client.get_request(
            "https://api.developer.legrand.com/hc/api/v1.0/plants/"
        )
    )
    plant_info = loop.run_until_complete(resp.json())

    # Retrieve the first and only plant in the response
    p = plant_info["plants"][0]
    test_plant = homeplusplant.HomePlusPlant(
        p["id"], p["name"], p["country"], test_client
    )

    plant_str = (
        "Home+ Plant: name->My Home, id->123456789009876543210, country->ES"
    )
    assert test_plant.__str__() == plant_str

    # Now read the topology
    loop.run_until_complete(test_plant.update_topology())
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
    assert len(test_plant.modules) == 10
    assert len(plugs) == 3
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2

    for mod in test_plant.modules.values():
        assert not mod.reachable

    # Now we read the status, but this returns error
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

    # Modules are still there
    assert len(test_plant.modules) == 10
    assert len(plugs) == 3
    assert len(lights) == 2
    assert len(remotes) == 3
    assert len(automations) == 2

    # But remain unreachable
    for mod in test_plant.modules.values():
        assert not mod.reachable
