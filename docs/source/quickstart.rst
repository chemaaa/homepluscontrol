.. _quickstart:

Quickstart
==========
Install ``homepluscontrol`` using ``pip``: 

``$ pip install homepluscontrol``. 


Usage Example
-------------
The following script is a simple example of how this Python library can be used::

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
        result = await client.request('get', protected_url)
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