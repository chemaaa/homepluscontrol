import asyncio
from homepluscontrol import homeplusplant, homeplusmodule, homeplusplug, homepluslight, homeplusremote
import json
from . import fixtures

class MockOAuthClient():

    def __init__(self, status_method):
        self.data = status_method()

    async def get_request(self, url, **kwargs):
        return MockResponse(self.data)

    async def post_request(self, url, data, **kwargs):
        return MockResponse(self.data)

class MockResponse():

    def __init__(self, data):
        self.data = data

    async def json(self):
        return json.loads(self.data)


mock_plant = homeplusplant.HomePlusPlant(id = "mock_plant_1",
                                         name = "Mock Plant",
                                         country = "The World",
                                         oauth_client = MockOAuthClient(fixtures.plug_status))

test_module = homeplusmodule.HomePlusModule(plant = mock_plant,
                                       id = "module_id",
                                       name = "Test Module 1",
                                       hw_type = "HW type 1",
                                       device = "Base Module",
                                       fw = "FW1",
                                       type = "Base Module Type")

plug_module = homeplusplug.HomePlusPlug(plant = mock_plant,
                                       id = "module_id_2",
                                       name = "Plug Module 1",
                                       hw_type = "HW type 2",
                                       device = "Plug",
                                       fw = "FW2",
                                       type = "Plug Module Type")

light_module = homepluslight.HomePlusLight(plant = mock_plant,
                                       id = "module_id_3",
                                       name = "Light Module 1",
                                       hw_type = "HW type 3",
                                       device = "Light",
                                       fw = "FW3",
                                       type = "Light Module Type")

remote_module = homeplusremote.HomePlusRemote(plant = mock_plant,
                                       id = "module_id_4",
                                       name = "Remote Module 1",
                                       hw_type = "HW type 4",
                                       device = "Remote",
                                       fw = "FW4",
                                       type = "Remote Module Type")

### Plant Tests
def test_plant_str():
    plant_str = "Home+ Plant: name->Mock Plant, id->mock_plant_1, country->The World"
    assert mock_plant.__str__() == plant_str

def test_topology_and_module_update():
    loop = asyncio.get_event_loop()

    async def test_coroutine():
        mock_plant.oauth_client = MockOAuthClient(fixtures.plant_topology)
        await mock_plant.refresh_topology()
        mock_plant.oauth_client = MockOAuthClient(fixtures.plant_modules)
        await mock_plant.refresh_module_status()
        mock_plant._parse_topology_and_modules()

    loop.run_until_complete(test_coroutine())
    assert isinstance(mock_plant.modules['0000000987654321fedcba'], homeplusplug.HomePlusPlug)
    assert mock_plant.modules['0000000787654321fedcba'].name == 'Living Room Ceiling Light'

### Base Module Tests
def test_base_module_url():
    test_module.build_status_url("https://dummy.com:1123/")    
    assert test_module.statusUrl == "https://dummy.com:1123/mock_plant_1/modules/parameter/id/value/module_id"

def test_base_module_str():
    module_str = "Home+ Module: device->Base Module, name->Test Module 1, id->module_id, reachable->False"
    assert test_module.__str__() == module_str

def test_base_update_status():
    mock_plant.oauth_client = MockOAuthClient(fixtures.plug_status)
    loop = asyncio.get_event_loop()

    async def test_coroutine():
        result = await test_module.get_status_update()
        return result
    
    status_result = loop.run_until_complete(test_coroutine())
    assert status_result['reachable']
    assert status_result['fw'] != None

### Plug Module Tests
def test_plug_module_url():    
    assert plug_module.statusUrl == "https://api.developer.legrand.com/hc/api/v1.0/plug/energy/addressLocation/plants/mock_plant_1/modules/parameter/id/value/module_id_2"

def test_plug_module_str():
    module_str = "Home+ Plug: device->Plug, name->Plug Module 1, id->module_id_2, reachable->False, status->"
    assert plug_module.__str__() == module_str

def test_plug_update_status():
    mock_plant.oauth_client = MockOAuthClient(fixtures.plug_status)
    loop = asyncio.get_event_loop()

    async def test_coroutine():
        result = await plug_module.get_status_update()
        return result
    
    status_result = loop.run_until_complete(test_coroutine())
    assert status_result['reachable']
    assert status_result['fw'] != None
    assert status_result['status'] == 'on'

def test_plug_turn_on():
    mock_plant.oauth_client = MockOAuthClient(fixtures.plug_status)
    loop = asyncio.get_event_loop()

    async def test_coroutine():
        result = await plug_module.turn_on()
        return result
    
    status_result = loop.run_until_complete(test_coroutine())
    assert plug_module.status == 'on'

def test_plug_turn_off():
    mock_plant.oauth_client = MockOAuthClient(fixtures.plug_status)
    loop = asyncio.get_event_loop()

    async def test_coroutine():
        result = await plug_module.turn_off()
        return result
    
    status_result = loop.run_until_complete(test_coroutine())
    assert plug_module.status == 'off'

def test_plug_toggle():
    mock_plant.oauth_client = MockOAuthClient(fixtures.plug_status)
    loop = asyncio.get_event_loop()

    async def test_coroutine():
        result = await plug_module.turn_on()
        result = await plug_module.toggle_status()
        return result
    
    status_result = loop.run_until_complete(test_coroutine())
    assert plug_module.status == 'off'

### Light Module Tests
def test_light_module_url():  
    assert light_module.statusUrl == "https://api.developer.legrand.com/hc/api/v1.0/light/lighting/addressLocation/plants/mock_plant_1/modules/parameter/id/value/module_id_3"

def test_light_module_str():
    module_str = "Home+ Light: device->Light, name->Light Module 1, id->module_id_3, reachable->False, status->"
    assert light_module.__str__() == module_str

def test_light_update_status():
    mock_plant.oauth_client = MockOAuthClient(fixtures.light_status)
    loop = asyncio.get_event_loop()

    async def test_coroutine():
        result = await light_module.get_status_update()
        return result
        
    status_result = loop.run_until_complete(test_coroutine())    
    assert status_result['reachable']
    assert status_result['fw'] != None
    assert status_result['status'] == 'off'

def test_light_turn_on():
    mock_plant.oauth_client = MockOAuthClient(fixtures.light_status)
    loop = asyncio.get_event_loop()

    async def test_coroutine():
        result = await light_module.turn_on()
        return result
    
    status_result = loop.run_until_complete(test_coroutine())
    assert light_module.status == 'on'

def test_light_turn_off():
    mock_plant.oauth_client = MockOAuthClient(fixtures.light_status)
    loop = asyncio.get_event_loop()

    async def test_coroutine():
        result = await light_module.turn_off()
        return result
    
    status_result = loop.run_until_complete(test_coroutine())
    assert light_module.status == 'off'

def test_light_toggle():
    mock_plant.oauth_client = MockOAuthClient(fixtures.light_status)
    loop = asyncio.get_event_loop()

    async def test_coroutine():
        result = await light_module.turn_on()
        result = await light_module.toggle_status()
        return result
    
    status_result = loop.run_until_complete(test_coroutine())
    assert light_module.status == 'off'

### Remote Module Tests
def test_remote_module_url():    
    assert remote_module.statusUrl == "https://api.developer.legrand.com/hc/api/v1.0/remote/remote/addressLocation/plants/mock_plant_1/modules/parameter/id/value/module_id_4"

def test_remote_module_str():
    module_str = "Home+ Remote: device->Remote, name->Remote Module 1, id->module_id_4, reachable->False, battery->"
    assert remote_module.__str__() == module_str

def test_remote_update_status():
    mock_plant.oauth_client = MockOAuthClient(fixtures.remote_status) 
    loop = asyncio.get_event_loop()

    async def test_coroutine():
        result = await remote_module.get_status_update()
        return result
    
    status_result = loop.run_until_complete(test_coroutine())
    assert not status_result['reachable']
    assert status_result['fw'] != None
    assert status_result['battery'] == 'full'
