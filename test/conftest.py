import asyncio
import re
import time

import pytest
from aioresponses import aioresponses
from homepluscontrol import (
    authentication,
    homepluslight,
    homeplusmodule,
    homeplusplant,
    homeplusplug,
    homeplusremote,
    homeplusautomation,
)


# Test fixtures
client_id = "client_identifier"
client_secret = "client_secret"
redirect_uri = "https://www.dummy.com:1123/auth"
token = {
    "access_token": "AcCeSs_ToKeN",
    "refresh_token": "ReFrEsH_ToKeN",
    "expires_in": -1,
    "expires_on": time.time() + 500,
}


@pytest.fixture()
def test_client():
    async def create_client():
        return authentication.HomePlusOAuth2Async(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            token=token,
        )

    async def close_client(client):
        await client.oauth_client.close()

    loop = asyncio.get_event_loop()
    client = loop.run_until_complete(create_client())
    yield client
    loop.run_until_complete(close_client(client))


@pytest.fixture()
def plant_data():
    return """
{"body":
    {"homes":[
        {
            "id":"123456789009876543210",
            "name":"My Home",
            "altitude":100,
            "coordinates":[0.000,0.000],
            "country":"ES",
            "timezone":"Europe/Madrid",
            "rooms":[
                {"id":"4560", "name":"Master Bedroom", "type":"bedroom", "module_ids":["aa:87:65:43:21:fe:dc:ba", "aa:88:99:43:18:1f:09:76", "aa:34:97:56:13:cc:bb:aa"]},
                {"id":"9885", "name":"Living Room", "type":"livingroom", "module_ids":["aa:04:74:00:00:0b:ab:cd", "aa:23:45:00:00:ab:cd:fe", "aa:11:11:32:11:ae:df:11"]},
                {"id":"8756", "name":"Dining Room", "type":"dining_room", "module_ids":["aa:77:11:43:18:de:df:12", "aa:23:98:32:11:ae:ff:ad"]},
                {"id":"1221", "name":"Kitchen", "type":"kitchen", "module_ids":["aa:34:56:78:90:00:0c:dd", "aa:45:21:aa:1b:fc:bd:da" , "aa:34:ab:f3:ff:4e:22:b1"]}
            ],
            "modules":[
                {"id":"00:11:22:33:44:55", "type":"NLG", "name":"Gateway", "setup_date":1563480130, "room_id":"9885",
                    "modules_bridged":[
                        "aa:04:74:00:00:0b:ab:cd",
                        "aa:23:45:00:00:ab:cd:fe",
                        "aa:87:65:43:21:fe:dc:ba",
                        "aa:23:98:32:11:ae:ff:ad",
                        "aa:11:11:32:11:ae:df:11",
                        "aa:77:11:43:18:de:df:12",
                        "aa:34:56:78:90:00:0c:dd",
                        "aa:88:99:43:18:1f:09:76",
                        "aa:34:97:56:13:cc:bb:aa",
                        "aa:45:21:aa:1b:fc:bd:da",
                        "aa:34:ab:f3:ff:4e:22:b1"
                    ]
                },
                {"id":"aa:04:74:00:00:0b:ab:cd", "type":"NLP", "name":"Gateway Plug", "setup_date":1563480133, "room_id":"9885", "bridge":"00:11:22:33:44:55", "appliance_type":"other"},
                {"id":"aa:23:45:00:00:ab:cd:fe", "type":"NLT", "name":"General Command", "setup_date":1563480133, "room_id":"9885", "bridge":"00:11:22:33:44:55"},
                {"id":"aa:87:65:43:21:fe:dc:ba", "type":"NLP", "name":"Bedroom Wall Outlet", "setup_date":1563480133, "room_id":"4560", "bridge":"00:11:22:33:44:55", "appliance_type":"other"},
                {"id":"aa:34:ab:f3:ff:4e:22:b1", "type":"NLP", "name":"Kitchen Wall Outlet", "setup_date":1563480133, "room_id":"1221", "bridge":"00:11:22:33:44:55", "appliance_type":"other"},
                {"id":"aa:23:98:32:11:ae:ff:ad", "type":"NLP", "name":"Dining Room Wall Outlet", "setup_date":1563561592, "room_id":"8756", "bridge":"00:11:22:33:44:55", "appliance_type":"other"},
                {"id":"aa:11:11:32:11:ae:df:11", "type":"NLF", "name":"Living Room Ceiling Light", "setup_date":1607024740, "room_id":"9885", "bridge":"00:11:22:33:44:55"},
                {"id":"aa:77:11:43:18:de:df:12", "type":"NLF", "name":"Dining Room Ceiling Light", "setup_date":1607024740, "room_id":"8756", "bridge":"00:11:22:33:44:55"},
                {"id":"aa:34:56:78:90:00:0c:dd", "type":"NBR", "name":"Volet Cuisine", "setup_date":1607028610, "room_id":"1221", "bridge":"00:11:22:33:44:55"},
                {"id":"aa:88:99:43:18:1f:09:76", "type":"NBR", "name":"Volet Chambre", "setup_date":1607028825, "room_id":"4560", "bridge":"00:11:22:33:44:55"},
                {"id":"aa:34:97:56:13:cc:bb:aa", "type":"NLT", "name":"Wall Switch 1", "setup_date":1619255091, "room_id":"4560", "bridge":"00:11:22:33:44:55"},
                {"id":"aa:45:21:aa:1b:fc:bd:da", "type":"NLT", "name":"Wall Switch 2", "setup_date":1619255534, "room_id":"1221", "bridge":"00:11:22:33:44:55"}
            ],
            "temperature_control_mode":"heating",
            "therm_mode":"schedule",
            "therm_setpoint_default_duration":180,
            "schedules":[
                {
                    "timetable":[],
                    "zones":[],
                    "name":"Actions schedule",
                    "default":false,
                    "timetable_sunrise":[],
                    "timetable_sunset":[],
                    "id":"abcdef1234",
                    "selected":true,
                    "type":"event"
                },
                {"timetable":[
                        {"zone_id":1, "m_offset":0},
                        {"zone_id":0, "m_offset":420}
                    ],
                    "zones":[
                        {"id":0, "price":0.3, "price_type":"peak"},
                        {"id":1, "price":0.1, "price_type":"off_peak"}
                    ],
                    "name":"electricity",
                    "default":false,
                    "tariff":"custom",
                    "tariff_option":"peak_and_off_peak",
                    "power_threshold":6.9,
                    "contract_power_unit":"kW",
                    "id":"132133bbbdef",
                    "selected":true,
                    "type":"electricity"
                }
            ]
        }
        ], "user":{
            "email":"user.email@domain.com",
            "language":"en",
            "locale":"en-US",
            "feel_like_algorithm":0,
            "unit_pressure":0,
            "unit_system":0,
            "unit_wind":0,
            "id":"abcdef12345678901234567890fedcba"
        }
    },
    "status":"ok",
    "time_exec":1.0,
    "time_server":1654924120
}"""


@pytest.fixture()
def two_plant_data():
    return """
{"body":
    {"homes":[
        {
            "id":"123456789009876543210",
            "name":"My Home",
            "altitude":100,
            "coordinates":[0.000,0.000],
            "country":"ES",
            "timezone":"Europe/Madrid",
            "rooms":[],
            "modules":[],
            "temperature_control_mode":"heating",
            "therm_mode":"schedule",
            "therm_setpoint_default_duration":180,
            "schedules":[]
        },
        {
            "id":"99999999999999999999",
            "name":"Office",
            "altitude":100,
            "coordinates":[0.000,0.000],
            "country":"NL",
            "timezone":"Europe/Amsterdam",
            "rooms":[],
            "modules":[],
            "temperature_control_mode":"heating",
            "therm_mode":"schedule",
            "therm_setpoint_default_duration":180,
            "schedules":[]
        }
        ], "user":{
            "email":"user.email@domain.com",
            "language":"en",
            "locale":"en-US",
            "feel_like_algorithm":0,
            "unit_pressure":0,
            "unit_system":0,
            "unit_wind":0,
            "id":"abcdef12345678901234567890fedcba"
        }
    },
    "status":"ok",
    "time_exec":1.0,
    "time_server":1654924120
}   
    """


# Change in the plant topology
@pytest.fixture()
def plant_topology_reduced():
    return """
{"body":
    {"homes":[
        {
            "id":"123456789009876543210",
            "name":"My Home",
            "altitude":100,
            "coordinates":[0.000,0.000],
            "country":"ES",
            "timezone":"Europe/Madrid",
            "rooms":[
                {"id":"4560", "name":"Master Bedroom", "type":"bedroom", "module_ids":["aa:87:65:43:21:fe:dc:ba", "aa:88:99:43:18:1f:09:76", "aa:34:97:56:13:cc:bb:aa"]},
                {"id":"9885", "name":"Living Room", "type":"livingroom", "module_ids":["aa:04:74:00:00:0b:ab:cd", "aa:23:45:00:00:ab:cd:fe", "aa:11:11:32:11:ae:df:11"]},
                {"id":"8756", "name":"Dining Room", "type":"dining_room", "module_ids":["aa:77:11:43:18:de:df:12", "aa:23:98:32:11:ae:ff:ad"]},
                {"id":"1221", "name":"Kitchen", "type":"kitchen", "module_ids":["aa:34:56:78:90:00:0c:dd", "aa:45:21:aa:1b:fc:bd:da" , "aa:34:ab:f3:ff:4e:22:b1"]}
            ],
            "modules":[
                {"id":"00:11:22:33:44:55", "type":"NLG", "name":"Gateway", "setup_date":1563480130, "room_id":"9885",
                    "modules_bridged":[
                        "aa:04:74:00:00:0b:ab:cd",
                        "aa:23:45:00:00:ab:cd:fe",
                        "aa:87:65:43:21:fe:dc:ba",
                        "aa:23:98:32:11:ae:ff:ad",
                        "aa:11:11:32:11:ae:df:11",
                        "aa:34:56:78:90:00:0c:dd",
                        "aa:34:97:56:13:cc:bb:aa"
                    ]
                },
                {"id":"aa:04:74:00:00:0b:ab:cd", "type":"NLP", "name":"Gateway Plug", "setup_date":1563480133, "room_id":"9885", "bridge":"00:11:22:33:44:55", "appliance_type":"other"},
                {"id":"aa:23:45:00:00:ab:cd:fe", "type":"NLT", "name":"General Command", "setup_date":1563480133, "room_id":"9885", "bridge":"00:11:22:33:44:55"},
                {"id":"aa:87:65:43:21:fe:dc:ba", "type":"NLP", "name":"Bedroom Wall Outlet", "setup_date":1563480133, "room_id":"4560", "bridge":"00:11:22:33:44:55", "appliance_type":"other"},
                {"id":"aa:23:98:32:11:ae:ff:ad", "type":"NLP", "name":"Dining Room Wall Outlet", "setup_date":1563561592, "room_id":"8756", "bridge":"00:11:22:33:44:55", "appliance_type":"other"},
                {"id":"aa:11:11:32:11:ae:df:11", "type":"NLF", "name":"Living Room Ceiling Light", "setup_date":1607024740, "room_id":"9885", "bridge":"00:11:22:33:44:55"},                
                {"id":"aa:34:56:78:90:00:0c:dd", "type":"NBR", "name":"Volet Cuisine", "setup_date":1607028610, "room_id":"1221", "bridge":"00:11:22:33:44:55"},
                {"id":"aa:34:97:56:13:cc:bb:aa", "type":"NLT", "name":"Wall Switch 1", "setup_date":1619255091, "room_id":"4560", "bridge":"00:11:22:33:44:55"}            ],
            "temperature_control_mode":"heating",
            "therm_mode":"schedule",
            "therm_setpoint_default_duration":180,
            "schedules":[
                {
                    "timetable":[],
                    "zones":[],
                    "name":"Actions schedule",
                    "default":false,
                    "timetable_sunrise":[],
                    "timetable_sunset":[],
                    "id":"abcdef1234",
                    "selected":true,
                    "type":"event"
                },
                {"timetable":[
                        {"zone_id":1, "m_offset":0},
                        {"zone_id":0, "m_offset":420}
                    ],
                    "zones":[
                        {"id":0, "price":0.3, "price_type":"peak"},
                        {"id":1, "price":0.1, "price_type":"off_peak"}
                    ],
                    "name":"electricity",
                    "default":false,
                    "tariff":"custom",
                    "tariff_option":"peak_and_off_peak",
                    "power_threshold":6.9,
                    "contract_power_unit":"kW",
                    "id":"132133bbbdef",
                    "selected":true,
                    "type":"electricity"
                }
            ]
        }
        ], "user":{
            "email":"user.email@domain.com",
            "language":"en",
            "locale":"en-US",
            "feel_like_algorithm":0,
            "unit_pressure":0,
            "unit_system":0,
            "unit_wind":0,
            "id":"abcdef12345678901234567890fedcba"
        }
    },
    "status":"ok",
    "time_exec":1.0,
    "time_server":1654924120
}"""


@pytest.fixture()
def plant_modules():
    return """
    {
    "status": "ok",
    "time_server": 1656139596,
    "body": {
        "home": {
            "id": "123456789009876543210",
            "modules": [
                {
                    "id": "00:11:22:33:44:55",
                    "type": "NLG",
                    "offload": false,
                    "firmware_revision": 250,
                    "last_seen": 1656136223,
                    "wifi_strength": 70,
                    "reachable": true
                },
                {
                    "id": "aa:04:74:00:00:0b:ab:cd",
                    "type": "NLP",
                    "on": true,
                    "offload": false,
                    "firmware_revision": 68,
                    "last_seen": 1656139415,
                    "power": 0,
                    "reachable": true,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:23:45:00:00:ab:cd:fe",
                    "type": "NLT",
                    "battery_state": "full",
                    "battery_level": 2600,
                    "firmware_revision": 42,
                    "last_seen": 0,
                    "reachable": true,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:87:65:43:21:fe:dc:ba",
                    "type": "NLP",
                    "on": true,
                    "offload": false,
                    "firmware_revision": 68,
                    "last_seen": 1656139436,
                    "power": 3,
                    "reachable": true,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:34:ab:f3:ff:4e:22:b1",
                    "type": "NLP",
                    "on": true,
                    "offload": false,
                    "firmware_revision": 68,
                    "last_seen": 1656139501,
                    "power": 2,
                    "reachable": true,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:11:11:32:11:ae:df:11",
                    "type": "NLF",
                    "on": false,
                    "firmware_revision": 46,
                    "last_seen": 1656139590,
                    "power": 0,
                    "reachable": true,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:77:11:43:18:de:df:12",
                    "type": "NLF",
                    "on": false,
                    "firmware_revision": 57,
                    "last_seen": 1656139187,
                    "power": 18,
                    "reachable": true,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:23:98:32:11:ae:ff:ad",
                    "type": "NLP",
                    "on": true,
                    "firmware_revision": 49,
                    "last_seen": 1656139306,
                    "power": 1999,
                    "reachable": true,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:34:56:78:90:00:0c:dd",
                    "type": "NBR",
                    "firmware_revision": 59,
                    "last_seen": 1656135719,
                    "reachable": true,
                    "current_position": 100,
                    "target_position": 100,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:88:99:43:18:1f:09:76",
                    "type": "NBR",
                    "firmware_revision": 57,
                    "last_seen": 1656139150,
                    "reachable": true,
                    "current_position": 0,
                    "target_position": 0,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:34:97:56:13:cc:bb:aa",
                    "type": "NLT",
                    "battery_state": "full",
                    "battery_level": 3300,
                    "firmware_revision": 59,
                    "last_seen": 1655875966,
                    "reachable": true,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:45:21:aa:1b:fc:bd:da",
                    "type": "NLT",
                    "battery_state": "full",
                    "battery_level": 2900,
                    "firmware_revision": 55,
                    "last_seen": 1656013360,
                    "reachable": true,
                    "bridge": "00:11:22:33:44:55"
                }
            ]
        }
    }
}
    """


# Change the module status response
@pytest.fixture()
def plant_modules_reduced():
    return """
    {
    "status": "ok",
    "time_server": 1656139596,
    "body": {
        "home": {
            "id": "123456789009876543210",
            "modules": [
                {
                    "id": "00:11:22:33:44:55",
                    "type": "NLG",
                    "offload": false,
                    "firmware_revision": 250,
                    "last_seen": 1656136223,
                    "wifi_strength": 70,
                    "reachable": true
                },
                {
                    "id": "aa:04:74:00:00:0b:ab:cd",
                    "type": "NLP",
                    "on": true,
                    "offload": false,
                    "firmware_revision": 68,
                    "last_seen": 1656139415,
                    "power": 0,
                    "reachable": true,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:23:45:00:00:ab:cd:fe",
                    "type": "NLT",
                    "battery_state": "full",
                    "battery_level": 2600,
                    "firmware_revision": 42,
                    "last_seen": 0,
                    "reachable": false,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:87:65:43:21:fe:dc:ba",
                    "type": "NLP",
                    "on": true,
                    "offload": false,
                    "firmware_revision": 68,
                    "last_seen": 1656139436,
                    "power": 3,
                    "reachable": true,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:77:11:43:18:de:df:12",
                    "type": "NLF",
                    "on": false,
                    "firmware_revision": 57,
                    "last_seen": 1656139187,
                    "power": 18,
                    "reachable": true,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:23:98:32:11:ae:ff:ad",
                    "type": "NLP",
                    "on": true,
                    "firmware_revision": 49,
                    "last_seen": 1656139306,
                    "power": 1999,
                    "reachable": true,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:34:56:78:90:00:0c:dd",
                    "type": "NBR",
                    "firmware_revision": 59,
                    "last_seen": 1656135719,
                    "reachable": true,
                    "current_position": 100,
                    "target_position": 100,
                    "bridge": "00:11:22:33:44:55"
                },
                {
                    "id": "aa:34:97:56:13:cc:bb:aa",
                    "type": "NLT",
                    "battery_state": "full",
                    "battery_level": 3300,
                    "firmware_revision": 59,
                    "last_seen": 1655875966,
                    "reachable": true,
                    "bridge": "00:11:22:33:44:55"
                }
            ]
        }
    }
}
    """


@pytest.fixture()
def mock_plant_aioresponse(plant_data, two_plant_data, plant_modules):
    with aioresponses() as mock:
        mock.get(
            "https://api.netatmo.com/api/homesdata",
            status=200,
            body=plant_data,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=200,
            body=plant_modules,
        )

        # Second set of calls
        mock.get(
            "https://api.netatmo.com/api/homesdata",
            status=200,
            body=two_plant_data,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=200,
            body=plant_modules,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=99999999999999999999",
            status=200,
            body=plant_modules,
        )

        # Third set of calls
        mock.get(
            "https://api.netatmo.com/api/homesdata",
            status=200,
            body=plant_data,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=200,
            body=plant_modules,
        )

        yield mock


@pytest.fixture()
def mock_aioresponse(
    plant_data,
    plant_modules,
):
    with aioresponses() as mock:
        mock.get(
            "https://api.netatmo.com/api/homesdata",
            status=200,
            body=plant_data,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=200,
            body=plant_modules,
        )

        mock.post(
            "https://api.netatmo.com/api/setstate",
            status=200,
        )

        mock.post(
            "https://api.netatmo.com/api/setstate",
            status=200,
        )

        # Second set of calls
        mock.get(
            "https://api.netatmo.com/api/homesdata",
            status=200,
            body=plant_data,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=200,
            body=plant_modules,
        )

        # Third set of calls
        mock.get(
            "https://api.netatmo.com/api/homesdata",
            status=200,
            body=plant_data,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=200,
            body=plant_modules,
        )

        yield mock


@pytest.fixture()
def error_aioresponse():
    pattern = re.compile(r"^https://api.netatmo.com/api.*$")
    with aioresponses() as mock:
        mock.get(pattern, status=400)  # Invalid arguments
        mock.get(pattern, status=403)  # Operation forbidden
        mock.get(pattern, status=404)  # Not found
        mock.get(pattern, status=406)  # Request not acceptable
        mock.get(pattern, status=500)  # Internal error
        yield mock


@pytest.fixture()
def test_plant(test_client):
    return homeplusplant.HomePlusPlant(
        id="mock_plant_1",
        home_data={"id": "mock_plant_1", "name": "Mock Plant", "country": "The World"},
        oauth_client=test_client,
    )


@pytest.fixture()
def test_module(test_plant):
    return homeplusmodule.HomePlusModule(
        plant=test_plant,
        id="module_id",
        name="Test Module 1",
        hw_type="HW type 1",
        device="Base Module",
        fw="FW1",
        type="Base Module Type",
        bridge="00:11:22:33:44:55",
    )


@pytest.fixture()
def test_plug(test_plant):
    return homeplusplug.HomePlusPlug(
        plant=test_plant,
        id="module_id_2",
        name="Plug Module 1",
        hw_type="HW type 2",
        device="Plug",
        fw="FW2",
        type="Plug Module Type",
        bridge="00:11:22:33:44:55",
    )


@pytest.fixture()
def test_light(test_plant):
    return homepluslight.HomePlusLight(
        plant=test_plant,
        id="module_id_3",
        name="Light Module 1",
        hw_type="HW type 3",
        device="Light",
        fw="FW3",
        type="Light Module Type",
        bridge="00:11:22:33:44:55",
    )


@pytest.fixture()
def test_remote(test_plant):
    return homeplusremote.HomePlusRemote(
        plant=test_plant,
        id="module_id_4",
        name="Remote Module 1",
        hw_type="HW type 4",
        device="Remote",
        fw="FW4",
        type="Remote Module Type",
        bridge="00:11:22:33:44:55",
    )


@pytest.fixture()
def test_automation(test_plant):
    return homeplusautomation.HomePlusAutomation(
        plant=test_plant,
        id="module_id_5",
        name="Automation Module 1",
        hw_type="HW type 5",
        device="Automation",
        fw="FW5",
        type="Automation Module Type",
        bridge="00:11:22:33:44:55",
    )


@pytest.fixture()
def mock_reduced_aioresponse(
    plant_data,
    plant_modules,
    plant_topology_reduced,
    plant_modules_reduced,
):
    with aioresponses() as mock:
        mock.get(
            "https://api.netatmo.com/api/homesdata",
            status=200,
            body=plant_data,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=200,
            body=plant_modules,
        )

        # Second set of calls with reduced topology
        mock.get(
            "https://api.netatmo.com/api/homesdata",
            status=200,
            body=plant_topology_reduced,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=200,
            body=plant_modules_reduced,
        )

        yield mock


@pytest.fixture()
def mock_growing_aioresponse(
    plant_data,
    plant_modules,
    plant_topology_reduced,
    plant_modules_reduced,
):
    with aioresponses() as mock:
        mock.get(
            "https://api.netatmo.com/api/homesdata",
            status=200,
            body=plant_topology_reduced,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=200,
            body=plant_modules_reduced,
        )

        # Second set of calls with reduced topology
        mock.get(
            "https://api.netatmo.com/api/homesdata",
            status=200,
            body=plant_data,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=200,
            body=plant_modules,
        )

        yield mock


@pytest.fixture()
def mock_growing_plant_aioresponse(
    plant_data,
    plant_modules,
    plant_topology_reduced,
    plant_modules_reduced,
):
    with aioresponses() as mock:
        mock.get(
            "https://api.netatmo.com/api/homesdata",
            status=200,
            body=plant_topology_reduced,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=200,
            body=plant_modules_reduced,
        )

        # Second set of calls with reduced topology
        mock.get(
            "https://api.netatmo.com/api/homesdata",
            status=200,
            body=plant_data,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=200,
            body=plant_modules_reduced,
        )

        # Final set of calls
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=200,
            body=plant_modules,
        )

        yield mock


@pytest.fixture()
def partial_error_aioresponse(plant_data, plant_modules):
    with aioresponses() as mock:
        mock.get(
            "https://api.netatmo.com/api/homesdata",
            status=200,
            body=plant_data,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=500,
            body=plant_modules,
        )

        mock.get(
            "https://api.netatmo.com/api/homesdata",
            status=200,
            body=plant_data,
        )
        mock.get(
            "https://api.netatmo.com/api/homestatus?home_id=123456789009876543210",
            status=200,
            body=plant_modules,
        )

        yield mock


@pytest.fixture()
def async_mock_plant(mock_aioresponse, test_client):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(test_client.get_request("https://api.netatmo.com/api/homesdata"))
    response_body = loop.run_until_complete(resp.json())
    plant_info = response_body["body"]

    # Retrieve the first and only plant in the response
    p = plant_info["homes"][0]
    mock_plant = homeplusplant.HomePlusPlant(p["id"], p, test_client)

    # Read the modules into arrays
    loop.run_until_complete(mock_plant.update_module_status())
    return mock_plant, loop


@pytest.fixture()
def mock_automation_post():
    future = asyncio.Future()
    future.set_result(True)
    return future
