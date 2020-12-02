import asyncio
from homepluscontrol import authentication, homeplusplant, homeplusmodule, homeplusinteractivemodule, homeplusplug, homepluslight, homeplusremote
import json
from . import conftest
from aioresponses import aioresponses
import time


def setup_mock_plant(mock_aioresponse, test_client):
    loop = asyncio.get_event_loop()
    mock_plant = homeplusplant.HomePlusPlant("123456789009876543210", "My Home", "ES", test_client)
    loop.run_until_complete(mock_plant.update_topology_and_modules())
    return mock_plant, loop

### Plant Tests
def test_plant_str(test_plant):
    plant_str = "Home+ Plant: name->Mock Plant, id->mock_plant_1, country->The World"
    assert test_plant.__str__() == plant_str

def test_topology_and_module_update(mock_aioresponse, test_client):
    mock_plant = setup_mock_plant(mock_aioresponse, test_client)[0]
    assert isinstance(mock_plant.modules['0000000987654321fedcba'], homeplusplug.HomePlusPlug)
    assert mock_plant.modules['0000000787654321fedcba'].name == 'Living Room Ceiling Light'

### Base Module Tests
def test_base_module_url(test_module):
    test_module.build_status_url("https://dummy.com:1123/")    
    assert test_module.statusUrl == "https://dummy.com:1123/mock_plant_1/modules/parameter/id/value/module_id"

def test_base_module_str(test_module):
    module_str = "Home+ Module: device->Base Module, name->Test Module 1, id->module_id, reachable->False"
    assert test_module.__str__() == module_str

def test_base_update_status(mock_aioresponse, test_client):
    mock_plant, loop = setup_mock_plant(mock_aioresponse, test_client)
    mock_module = mock_plant.modules['0000000587654321fedcba']

    status_result = loop.run_until_complete(mock_module.get_status_update())
    assert isinstance(mock_module, homeplusmodule.HomePlusModule)
    assert status_result['reachable']
    assert status_result['fw'] != None

### Plug Module Tests
def test_plug_module_url(test_plug):    
    assert test_plug.statusUrl == "https://api.developer.legrand.com/hc/api/v1.0/plug/energy/addressLocation/plants/mock_plant_1/modules/parameter/id/value/module_id_2"

def test_plug_module_str(test_plug):
    module_str = "Home+ Plug: device->Plug, name->Plug Module 1, id->module_id_2, reachable->False, status->"
    assert test_plug.__str__() == module_str

def test_plug_update_status(mock_aioresponse, test_client):
    mock_plant, loop = setup_mock_plant(mock_aioresponse, test_client)
    mock_plug = mock_plant.modules['0000000587654321fedcba']
    
    status_result = loop.run_until_complete(mock_plug.get_status_update())
    assert isinstance(mock_plug, homeplusmodule.HomePlusModule)
    assert isinstance(mock_plug, homeplusinteractivemodule.HomePlusInteractiveModule)
    assert isinstance(mock_plug, homeplusplug.HomePlusPlug)
    assert status_result['reachable']
    assert status_result['fw'] != None
    assert status_result['status'] == 'on'

def test_plug_turn_on(mock_aioresponse, test_client):
    mock_plant, loop = setup_mock_plant(mock_aioresponse, test_client)
    mock_plug = mock_plant.modules['0000000587654321fedcba']
    
    status_result = loop.run_until_complete(mock_plug.turn_on())
    assert mock_plug.status == 'on'

def test_plug_turn_off(mock_aioresponse, test_client):
    mock_plant, loop = setup_mock_plant(mock_aioresponse, test_client)
    mock_plug = mock_plant.modules['0000000587654321fedcba']
    
    status_result = loop.run_until_complete(mock_plug.turn_off())
    assert mock_plug.status == 'off'

def test_plug_toggle(mock_aioresponse, test_client):
    mock_plant, loop = setup_mock_plant(mock_aioresponse, test_client)
    mock_plug = mock_plant.modules['0000000587654321fedcba']

    # Fixture light is on to start with
    status_result = loop.run_until_complete(mock_plug.toggle_status())
    assert mock_plug.status == 'off'

### Light Module Tests
def test_light_module_url(test_light):  
    assert test_light.statusUrl == "https://api.developer.legrand.com/hc/api/v1.0/light/lighting/addressLocation/plants/mock_plant_1/modules/parameter/id/value/module_id_3"

def test_light_module_str(test_light):
    module_str = "Home+ Light: device->Light, name->Light Module 1, id->module_id_3, reachable->False, status->"
    assert test_light.__str__() == module_str

def test_light_update_status(mock_aioresponse, test_client):
    mock_plant, loop = setup_mock_plant(mock_aioresponse, test_client)
    mock_light = mock_plant.modules['0000000787654321fedcba']
    
    status_result = loop.run_until_complete(mock_light.get_status_update())
    assert isinstance(mock_light, homeplusmodule.HomePlusModule)
    assert isinstance(mock_light, homeplusinteractivemodule.HomePlusInteractiveModule)
    assert isinstance(mock_light, homepluslight.HomePlusLight)
    assert status_result['reachable']
    assert status_result['fw'] != None
    assert status_result['status'] == 'off'

def test_light_turn_on(mock_aioresponse, test_client):
    mock_plant, loop = setup_mock_plant(mock_aioresponse, test_client)
    mock_light = mock_plant.modules['0000000787654321fedcba']
    
    status_result = loop.run_until_complete(mock_light.turn_on())
    assert mock_light.status == 'on'

def test_light_turn_off(mock_aioresponse, test_client):
    mock_plant, loop = setup_mock_plant(mock_aioresponse, test_client)
    mock_light = mock_plant.modules['0000000787654321fedcba']
    
    status_result = loop.run_until_complete(mock_light.turn_off())
    assert mock_light.status == 'off'

def test_light_toggle(mock_aioresponse, test_client):
    mock_plant, loop = setup_mock_plant(mock_aioresponse, test_client)
    mock_light = mock_plant.modules['0000000787654321fedcba']

    # Fixture light is off to start with
    status_result = loop.run_until_complete(mock_light.toggle_status())
    assert mock_light.status == 'on'

### Remote Module Tests
def test_remote_module_url(test_remote):    
    assert test_remote.statusUrl == "https://api.developer.legrand.com/hc/api/v1.0/remote/remote/addressLocation/plants/mock_plant_1/modules/parameter/id/value/module_id_4"

def test_remote_module_str(test_remote):
    module_str = "Home+ Remote: device->Remote, name->Remote Module 1, id->module_id_4, reachable->False, battery->"
    assert test_remote.__str__() == module_str

def test_remote_update_status(mock_aioresponse, test_client):
    mock_plant, loop = setup_mock_plant(mock_aioresponse, test_client)
    mock_remote = mock_plant.modules['000000012345678abcdef']

    status_result = loop.run_until_complete(mock_remote.get_status_update())
    assert isinstance(mock_remote, homeplusmodule.HomePlusModule)
    assert not isinstance(mock_remote, homeplusinteractivemodule.HomePlusInteractiveModule)
    assert isinstance(mock_remote, homeplusremote.HomePlusRemote)
    assert not status_result['reachable']
    assert status_result['fw'] != None
    assert status_result['battery'] == 'full'
