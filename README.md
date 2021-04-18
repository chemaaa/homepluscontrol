# Home + Control
This is a basic Python library that interacts with the *Legrand Home + Control* API. It is 
primarily intended for integration into Smart Home platforms such as Home Assistant.

More information of the API can be found here: https://developer.legrand.com/

The library currently supports 4 types of Legrand modules:

1) Plugs (power outlets)
2) Lights (connected switches)
3) Remotes (wireless switches)
4) Automations (shutters/covers)

The first two - plugs and lights - are modeled as basic switches that can be interacted with to set their status to *on* or *off*.
Remotes are presented as passive modules that only have a battery level attribute.
Automations can be issued commands to open or close to their full positions and to be stopped during the motion.

A 'home' is represented by a *plant* which presents all of its corresponding modules in a topology. A *plant* is basically a 
Legrand Home+ Control gateway.

The status of each module in the *plant* can be accessed through a single *status* call to the *plant* or through individual *status* 
calls to each module.

## Authentication
The *Legrand Home + Control* API uses Oauth2 authentication, so you must first register an account at https://developer.legrand.com/. 

Once registered, you will then need to create a subscription to the *Starter Kit* (currently the only subscription available) and this will
generate your SUBSCRIPTION_KEY.

As a final step, you will have to register an Application, where you will have to define a name, a redirect URL and the scopes of your application
(for simplicity you can mark all scopes). 

Once the Application is confirmed, you should receive an email containing the CLIENT_IDENTIFIER and
the CLIENT_SECRET which you will be using to set up the authentication flows.

### Authentication Flow
Communication with the API, first requires Oauth2 authentication to obtain an access and a refresh token. Subsequent requests to the API, require the use of the SUBSCRIPTION_KEY in addition to the access token.

Information about the Oauth2 exchange is provided here: https://developer.legrand.com/tutorials/0auth2-end-point-url/

## Quickstart
Install `homepluscontrol` using `pip`: 

    $ pip install homepluscontrol

### Usage Example
The following script is a simple example of how this Python library can be used::

```python
from homepluscontrol import authentication, homeplusplant
import asyncio

client_id = 'YOUR_CLIENT_IDENTIFIER'
client_secret = 'YOUR_CLIENT_SECRET'
subscription_key = 'YOUR_SUBSCRIPTION_KEY'
redirect_uri = 'https://www.example.com'

dummy_token = 
    {"refresh_token": 
        "dummy-refresh-token", 
        "access_token": "dummy-access-token", 
        "expires_at": -1, 
        "expires_on": -1}
api_plant_url = 'https://api.developer.legrand.com/hc/api/v1.0/plants'

# Create the asynchronous client to handle the authentication 
# process and the authenitcated requests
client = authentication.HomePlusOAuth2Async(client_id, 
                                            client_secret, 
                                            subscription_key, 
                                            token=dummy_token, 
                                            redirect_uri=redirect_uri)

# The URL returned by this method launches the Oauth2 flow and 
# allows a user to confirm the process.
# Doing so redirects the user's browser/client to the redirect URI
# and includes the code and the state for the next step.
authorization_url = client.generate_authorize_url()
print(authorization_url)

# Here is where you can enter the complete redirect URL
return_url = input('Redirect URL received:')

# This function will now handle the asynchronous calls to the API
async def interact_with_api():
    token = await client.async_fetch_initial_token(return_url)
    print(token)
    # The client now has a valid token and can be used 
    # to interact with the API.
    
    # First get the plant information
    result = await client.request('get', api_plant_url)
    plant_info = await result.json()
    print(plant_info)
    plant_array = []
    for p in plant_info['plants']:
        plant_array.append(
            homeplusplant.HomePlusPlant(p['id'], 
                                        p['name'], 
                                        p['country'], 
                                        client)
        )
    plant = plant_array[0]
    print(plant)
    
    # Next read the module information for the plant
    await plant.update_topology_and_modules()
    for mod_id in plant.modules.keys():
            print(plant.modules[mod_id])
    # Close the client session
    await client.oauth_client.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(interact_with_api())
```

## Testing
`homepluscontrol` tests are based on `pytest`. To run, change to the root directory of `homepluscontrol` and use the command: 

    $ pip install -r requirements.txt
    $ pip install -r requirements_test.txt
    $ pytest 