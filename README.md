# Home + Control
This is a basic Python library that interacts with the *Legrand Home + Control* API. It is 
primarily intended for integration into Smart Home platforms such as Home Assistant.

More information of the API can be found here: https://developer.legrand.com/

The library currently supports 3 types of Legrand modules:

1) Plugs (power outlets)
2) Lights (connected switches)
3) Remotes (wireless switches)

The first two - plugs and lights - are modeled as basic switches that can be interacted with to set their status to *on* or *off*.
Remotes are presented as passive modules that only have a battery level attribute.

A 'home' is represented by a *plant* which presents all of its corresponding modules in a topology. A *plant* is basically a 
Legrand Home+ Control gateway.

The status of each module in the *plant* can be accessed through a single *status* call to the *plant* or through individual *status* 
calls to each module.

## Authentication
The *Legrand Home + Control* API uses Oauth2 authentication, so you must first register an account at https://developer.legrand.com/. 

Once registered, you will then need to create a subscrption to the *Starter Kit* (currently the only subscription available) and this will
generate your SUBSCRIPTION_KEY.

As a final step, you will have to register an Application, where you will have to define a name, a redirect URL and the scopes of your application
(for simplicity you can mark all scopes). Once the Application is confirmed, you should receive an email containing the CLIENT_IDENTIFIER and
the CLIENT_SECRET which you will be using to set up the authentication flows.

## Quickstart
Install `homepluscontrol` using `pip`: `$ pip install homepluscontrol`. 

## Testing
`homepluscontrol` tests are based on `pytest`. To run, change to the root directory of `homepluscontrol` and use the command: `$ pytest`. 