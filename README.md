# Home + Control

**Legrand has deprecated the _Legrand Home + Control_ API and migrated to the _Netatmo Connect_ platform. This library has been updated to support the new _Netatmo Connect_ API.**

This is a basic Python library that interacts with the _Netatmo Connect Home + Control_ API. It is
primarily intended for integration into Smart Home platforms such as Home Assistant.

More information of the API can be found here: https://dev.netatmo.com/apidocumentation/control

The library currently supports 4 types of Legrand (not Smarther) modules:

1. Plugs (power outlets)
2. Lights (connected switches)
3. Remotes (wireless switches)
4. Automations (shutters/covers) [of the iDiamant/Bubbendorf product line]

The first two - plugs and lights - are modeled as basic switches that can be interacted with to set their status to _on_ or _off_.
Remotes are presented as passive modules that only have a battery level attribute.
Automations can be issued commands to open or close to their full positions and to be stopped during the motion.

A 'home' is represented by a _plant_ which presents all of its corresponding modules in a topology. A _plant_ is basically a Home+ Control gateway.

The status of each module in the _plant_ can be accessed through a single _status_ call to the _plant_ or through individual _status_ calls to each module.

## Authentication

The _Netatmo Connect Home + Control_ API uses Oauth2 authentication, so you must first register an account at https://dev.netatmo.com/.

Once registered, you will have to register an Application, where you will have to define a name and a redirect URL.

Once the Application is confirmed, you should receive the CLIENT_IDENTIFIER and the CLIENT_SECRET which you will be using to set up the authentication flows.

### Authentication Flow

Communication with the API, first requires Oauth2 authentication to obtain an access and a refresh token. Subsequent requests to the API will require the use of this access token.

Information about the Oauth2 exchange is provided here: https://dev.netatmo.com/apidocumentation/oauth

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
redirect_uri = 'https://www.example.com'

dummy_token =
    {"refresh_token":
        "dummy-refresh-token",
        "access_token": "dummy-access-token",
        "expires_at": -1,
        "expires_on": -1}
api_home_data_url = "https://api.netatmo.com/api/homesdata"

# Create the asynchronous client to handle the authentication
# process and the authenticated requests
client = authentication.HomePlusOAuth2Async(client_id,
                                            client_secret,
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

    # First get the home data
    result = await client.request("get", api_home_data_url)
    response_body = await result.json()
    homes_info = response_body["body"]
    print(homes_info)
    home_array = []
    for p in homes_info["homes"]:
        home_array.append(homeplusplant.HomePlusPlant(p["id"], p, client))
    home = home_array[0]
    print(home)

    # Next read the module information for the plant
    await home.update_module_status()
    for mod_id in home.modules.keys():
        print(home.modules[mod_id])

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
