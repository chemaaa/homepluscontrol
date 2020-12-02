from aioresponses import aioresponses
import asyncio
from homepluscontrol import authentication, homeplusplant, homeplusmodule, homeplusplug, homepluslight, homeplusremote
import time

# Integration tests
client_id = "client_identifier"
client_secret = "client_secret"
subscription_key = "subscription_key"
redirect_uri="https://www.dummy.com:1123/auth"
token = { "access_token" : "AcCeSs_ToKeN",
        "refresh_token" : "ReFrEsH_ToKeN",
        "expires_in" : -1,
        "expires_on" : time.time() + 500 }

client = authentication.HomePlusOAuth2Async(client_id = client_id,
                                        client_secret = client_secret,
                                        subscription_key = subscription_key,
                                        redirect_uri = redirect_uri,
                                        token = token)
                                        
def test_always_passes():
    assert True

def test_initial_plant_data(mock_aioresponse):
    loop = asyncio.get_event_loop()

    resp = loop.run_until_complete(client.get_request('https://api.developer.legrand.com/hc/api/v1.0/plants'))
    plant_info = loop.run_until_complete(resp.json())
    p = plant_info['plants'][0]
    mock_plant = homeplusplant.HomePlusPlant(p['id'], p['name'], p['country'], client)

    plant_str = "Home+ Plant: name->My Home, id->123456789009876543210, country->ES"
    assert mock_plant.__str__() == plant_str
