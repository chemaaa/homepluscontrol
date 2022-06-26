.. _authentication:

Authentication
==============
The *Netatmo Connect Home + Control*_* API uses Oauth2 authentication, so you must first register an account at https://dev.netatmo.com/.

Once registered, you will have to register an Application, where you will have to define a name and a redirect URL.

Once the Application is confirmed, you should receive the CLIENT_IDENTIFIER and the CLIENT_SECRET which you will be using to set up the authentication flows.


Authentication Flow
-------------------
Communication with the API, first requires Oauth2 authentication to obtain an access and a refresh token. Subsequent requests to the API will require the use of this access token.

Information about the Oauth2 exchange is provided here: https://dev.netatmo.com/apidocumentation/oauth




