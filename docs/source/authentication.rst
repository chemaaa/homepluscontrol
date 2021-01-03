.. _authentication:

Authentication
==============
The *Legrand Home + Control* API uses Oauth2 authentication, so you must first register an account at https://developer.legrand.com/. 

Once registered, you will then need to create a subscription to the *Starter Kit* (currently the only subscription available) and this will
generate your SUBSCRIPTION_KEY.

As a final step, you will have to register an Application, where you will have to define a name, a redirect URL and the scopes of your application
(for simplicity you can mark all scopes). 

Once the Application is confirmed, you should receive an email containing the CLIENT_IDENTIFIER andthe CLIENT_SECRET which you will be using 
to set up the authentication flows.


Authentication Flow
-------------------
Communication with the API, first requires Oauth2 authentication to obtain an access and a refresh token. 

Subsequent requests to the API, require the use of the SUBSCRIPTION_KEY in addition to the access token.

Information about the Oauth2 exchange is provided here: https://developer.legrand.com/tutorials/0auth2-end-point-url/




