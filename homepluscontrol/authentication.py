import logging
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
from aiohttp import ClientSession, ClientResponse
import asyncio
from yarl import URL
import secrets
import jwt
from typing import Any, Awaitable, Callable, Dict, Optional, cast
import re
import time

# Common definitions
AUTH_BASE_URL = 'https://partners-login.eliotbylegrand.com/authorize'
TOKEN_URL = REFRESH_URL = 'https://partners-login.eliotbylegrand.com/token'

class EliotOAuth2:
    """
    Handle authentication with OAuth2 - Synchronous Requests
    """

    def __init__(self, 
                 client_id, 
                 client_secret, 
                 subscription_key,  
                 token=None,
                 redirect_uri=None,
                 token_updater=None,
                ):

        self.client_id = client_id
        self.client_secret = client_secret
        self.subscription_key = subscription_key
        self.token = token
        self.redirect_uri = redirect_uri
        self.token_updater = token_updater

        self.extra = {"client_id": self.client_id, "client_secret": self.client_secret}
        self._subscription_header = { 'Ocp-Apim-Subscription-Key' : self.subscription_key }
        token_type = 'Bearer'

        self.oauth_client = OAuth2Session(
            client_id=self.client_id,
            token=token,
            token_updater=self.token_updater,
            redirect_uri=self.redirect_uri,
            auto_refresh_url=REFRESH_URL, 
            auto_refresh_kwargs=self.extra,
        )
    
    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    def refresh_tokens(self):
        """Refresh and return new access token"""
        self.logger.info("Access token is refreshing")
        self.token = self.oauth_client.refresh_token(REFRESH_URL, **self.extra)        
        if self.token_updater != None:
            self.token_updater(self.token)
        return self.token

    def request(self, method, url, **kwargs):
        """ Make an authenticated HTTP request """
        # Add the mandatory subscription key header to the request
        if 'headers' in kwargs:
            kwargs['headers'] = { **kwargs['headers'], **self._subscription_header }
        else:
            kwargs['headers'] = self._subscription_header
        try:
            return getattr(self.oauth_client, method)(url, **kwargs)
        except TokenExpiredError:
            self.logger.info("Request attempted on an expired token. Need to refresh.")
            print("Request attempted on an expired token. Need to refresh.")
            self.token = self.refresh_tokens()
            self.oauth_client.token = self.token
            return getattr(self.oauth_client, method)(url, **kwargs)
    
    def get_request(self, url, **kwargs):
        r = self.request('get', url, **kwargs)
        r.raise_for_status()
        return r

    def post_request(self, url, data, **kwargs):
        kwargs['data'] = data
        r = self.request('post', url, **kwargs)
        r.raise_for_status()
        return r

    def get_authorization_url(self):
        return self.oauth_client.authorization_url(AUTH_BASE_URL)

    def fetch_token(self, authorization_response=None):
        """
        Generic method for fetching an Eliot access token.
        :param authorization_response: Authorization response URL, the callback
                                       URL of the request back to you.
        :param code: Authorization code
        :return: A token dict
        """
        self.token = self.oauth_client.fetch_token(
            TOKEN_URL,
            authorization_response=authorization_response,
            client_secret=self.client_secret,
            include_client_id=True,
        )
        if self.token_updater != None:
            self.token_updater(self.token)
        return self.token


class EliotOAuth2Async:
    """
    Handle authentication with OAuth2 - Asynchronous Requests
    """

    def __init__(self, 
                 client_id, 
                 client_secret, 
                 subscription_key,  
                 token=None,
                 redirect_uri=None,
                 token_updater=None,
                ):

        self.client_id = client_id
        self.client_secret = client_secret
        self.subscription_key = subscription_key
        if token == None:
            token = { "expires_on": 0, "expires_in": -1, "access_token " : "dummy", "refresh_token" : "dummy" }
        self.token = token
        self.redirect_uri = redirect_uri
        self.token_updater = token_updater

        self.extra = {"client_id": self.client_id, "client_secret": self.client_secret}
        self._subscription_header = { 'Ocp-Apim-Subscription-Key' : self.subscription_key }
        self.token_type = 'Bearer'
        self.secret = secrets.token_hex()
        self.state = secrets.token_hex()

        self.oauth_client = ClientSession()
    
    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)
    
    @property
    def valid_token(self) -> bool:
        """Return if token is still valid."""
        expires_on = float(self.token["expires_on"])
        current_time = time.time()
        return (
             expires_on > current_time
        )
    
    def _encode_jwt(self, data: str) -> str:
        """JWT encode data."""        
        return jwt.encode(data, self.secret, algorithm="HS256").decode()

    def _decode_jwt(self, encoded: str) -> Optional[dict]:
        """JWT encode data."""
        secret = cast(str, self.secret)
        try:
            return jwt.decode(encoded, secret, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return None

    def _split_redirect_url(self, redirect_url):
        code_pattern = 'code=(.*)&'
        match = re.search(code_pattern, redirect_url)
        if match:
            code = {"code" :  match.group(1)}
        else:
            return None
        
        state_pattern='state=(.*)$'
        match = re.search(state_pattern, redirect_url)
        if match:
            state = self._decode_jwt(match.group(1))

        return { **code, **state }

    async def _async_refresh_token(self, token: dict) -> dict:
        """Refresh tokens."""
        new_token = await self._token_request(
            {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "refresh_token": token["refresh_token"],
            }
        )
        return {**token, **new_token}

    async def _token_request(self, data: dict) -> dict:
        """Make a token request."""
        data["client_id"] = self.client_id

        if self.client_secret is not None:
            data["client_secret"] = self.client_secret

        resp = await self.oauth_client.post(TOKEN_URL, data=data)
        resp.raise_for_status()
        
        self.token = cast(dict, await resp.json())
        if self.token_updater != None:
            await self.token_updater(self.token)
        return self.token

    def generate_authorize_url(self) -> str:
        """Generate a url for the user to authorize."""
        return str(
            URL(AUTH_BASE_URL)
            .with_query(
                {
                    "response_type": "code",
                    "client_id": self.client_id,
                    "redirect_uri": self.redirect_uri,
                    "state": self._encode_jwt( {"state": self.state} ),
                }
            )
        )

    async def async_ensure_token_valid(self) -> None:
        """Ensure that the current token is valid."""
        if self.valid_token:
            return
        return await self._async_refresh_token(self.token)

    async def async_fetch_initial_token(self, redirect_url: Any) -> dict:
        """Resolve the authorization code to tokens."""
        req_body = self._split_redirect_url(redirect_url)

        if req_body != None and req_body["state"] == self.state:
            return await self._token_request(
                {
                    "grant_type": "authorization_code",
                    "code": req_body["code"],
                }
            )
    
    async def request(self, method, url, **kwargs):
        """ Make an authenticated HTTP request """
        await self.async_ensure_token_valid()

        # Add the mandatory subscription key header to the request
        if 'headers' in kwargs:
            kwargs['headers'] = { **kwargs['headers'], **self._subscription_header }
        else:
            kwargs['headers'] = self._subscription_header

        kwargs['headers'] = { **kwargs['headers'], "authorization": f"Bearer {self.token['access_token']}" }
        return await self.oauth_client.request(method, url, **kwargs)
    
    async def get_request(self, url, **kwargs):
        r = await self.request('get', url, **kwargs)
        r.raise_for_status()
        return r

    async def post_request(self, url, data, **kwargs):
        kwargs['data'] = data
        r = await self.request('post', url, **kwargs)
        r.raise_for_status()
        return r
