import logging
import re
import secrets
import time
from abc import ABC, abstractmethod
from typing import Any, Optional, cast

import jwt
from aiohttp import ClientSession
from yarl import URL


class AbstractHomePlusOAuth2Async(ABC):
    def __init__(
        self,
        subscription_key,
        oauth_client=None,
    ):
        """AbstractHomePlusOAuth2Async Constructor.

        Base class to handle the OAuth2 authentication flow and HTTP
        asynchronous requests.
        Any class that extends this base class, should implement the method
        `async_get_access_token` to provide and refresh the OAuth2 access
        token accordingly.

        Based on aiohttp for asynchronous requests.

        Args:
            subscription_key (str): Subscription key obtained from
                                    the API provider
            oauth_client (:obj:`ClientSession`): aiohttp ClientSession object
                                                 that handles HTTP async
                                                 requests
        """
        self.subscription_key = subscription_key
        self._subscription_header = {
            "Ocp-Apim-Subscription-Key": self.subscription_key
        }

        if oauth_client is None:
            self.oauth_client = ClientSession()
        else:
            self.oauth_client = oauth_client

    @abstractmethod
    async def async_get_access_token(self) -> str:
        """Return a valid access token."""

    async def request(self, method, url, **kwargs):
        """Makes an authenticated async HTTP request.

        This method wraps around the aiohttp request method and adds the
        mandatory subscription key header that is required by the Home +
        Control API calls.

        Args:
            method (str): HTTP method to be used in the request (get, post,
                          put, delete)
            url (str): Endpoint of the HTTP request
            **kwargs (dict): Keyword arguments that will be forwarded to the
                             aiohttp request handler

        Returns:
            ClientResponse: aiohttp response object

        Raises:
            ClientError raised by aiohttp if it encounters an exceptional
            situation in the request
        """
        # Add the mandatory subscription key header to the request
        if "headers" in kwargs:
            kwargs["headers"] = {
                **kwargs["headers"],
                **self._subscription_header,
            }
        else:
            kwargs["headers"] = self._subscription_header

        await self.async_get_access_token()

        access_token = await self.async_get_access_token()
        kwargs["headers"] = {
            **kwargs["headers"],
            "authorization": f"Bearer {access_token}",
        }
        return await self.oauth_client.request(method, url, **kwargs)

    async def get_request(self, url, **kwargs):
        """Makes an authenticated async HTTP GET request.

        Shortcut method that relies on `request()` call and simply hardcodes
        the 'get' HTTP method

        Args:
            url (str): Endpoint of the HTTP request
            **kwargs(dict): Keyword arguments that will be forwarded to the
                            aiohttp request handler

        Returns:
            ClientResponse: aiohttp response object

        Raises:
            ClientError raised by aiohttp if it encounters an exceptional
            situation in the request
        """
        r = await self.request("get", url, **kwargs)
        r.raise_for_status()
        return r

    async def post_request(self, url, data, **kwargs):
        """Makes an authenticated async HTTP POST request.

        Shortcut method that relies on `request()` call and simply hardcodes
        the 'post' HTTP method

        Args:
            url (str): Endpoint of the HTTP request
            data (dict): Dictionary containing the parameters to be passed in
                         the POST request body
            **kwargs (dict): Keyword arguments that will be forwarded to the
                             aiohttp request handler

        Returns:
            ClientResponse: aiohttp response object

        Raises:
            ClientError raised by aiohttp if it encounters an exceptional
            situation in the request
        """
        kwargs["data"] = data
        r = await self.request("post", url, **kwargs)
        r.raise_for_status()
        return r


class HomePlusOAuth2Async(AbstractHomePlusOAuth2Async):
    """Handles authentication with OAuth2 - Uses aiohttp for asynchronous
    requests.

    This class is an implementation of the base class
    AbstractHomePlusOAuth2Async and so provides additional functions to
    request and manage the OAuth2 authentication flow and refresh access
    tokens when required.

    Attributes:
        client_id (str): Client identifier assigned by the API provider
                         when registering an app
        client_secret (str): Client secret assigned by the API provider
                             when registering an app
        subscription_key (str): Subscription key obtained from
                                the API provider
        token (dict): oauth2 token used by this authentication instance
        redirect_uri (str): URL for the redirection from
                            the authentication provider
        token_update (function): function that is called when a new token is
                                 obtained from the authentication provider
        oauth_client (:obj:`ClientSession`): aiohttp ClientSession object that
                                             handles HTTP async requests
    """

    # Authentication URLs for Legrant Home+ Control API
    AUTH_BASE_URL = "https://partners-login.eliotbylegrand.com/authorize"
    TOKEN_URL = REFRESH_URL = "https://partners-login.eliotbylegrand.com/token"

    def __init__(
        self,
        client_id,
        client_secret,
        subscription_key,
        token=None,
        redirect_uri=None,
        token_updater=None,
        oauth_client=None,
    ):
        """HomePlusOAuth2Async Constructor.

        Args:
            client_id (str): Client identifier assigned by the API provider
                             when registering an app
            client_secret (str): Client secret assigned by the API provider
                                 when registering an app
            subscription_key (str): Subscription key obtained from
                                    the API provider
            token (dict, optional): oauth2 token used by this authentication
                                    instance. Defaults to None.
            redirect_uri (str, optional): URL for the redirection from the
                                          authentication provider.
                                          Defaults to None
            token_update (function): function that is called when a new
                                     token is obtained from the
                                     authentication provider.
                                     Defaults to None
            oauth_client (ClientSession): aiohttp client session that
                                          handles asynchronous HTTP requests.
                                          If not specified, a new one is
                                          created. Defaults to None.
        """
        super().__init__(
            subscription_key=subscription_key,
            oauth_client=oauth_client,
        )
        self.client_id = client_id
        self.client_secret = client_secret
        if token is None:
            token = {
                "expires_on": 0,
                "expires_in": -1,
                "access_token ": "dummy",
                "refresh_token": "dummy",
            }
        self.token = token
        self.redirect_uri = redirect_uri
        self.token_updater = token_updater

        self._secret = secrets.token_hex()  # Used in JWT encode/decode
        self._state = secrets.token_hex()  # State string for token request

    @property
    def logger(self) -> logging.Logger:
        """Logger of authentication module."""
        return logging.getLogger(__name__)

    @property
    def valid_token(self) -> bool:
        """Current validity of the Oauth token (i.e. it has not expired).

        Return:
            True if the token is valid, False otherwise
        """
        expires_on = float(self.token["expires_on"])
        current_time = time.time()
        return expires_on > current_time

    def _encode_jwt(self, data: dict) -> str:
        """JWT encode data - relies on PyJWT.

        Args:
            data (dict): Dictionary containing the data that is to be encoded

        Returns:
            str: String of the encoded data.

        """
        encoded_str = jwt.encode(data, self._secret, algorithm="HS256")
        if isinstance(encoded_str, str):
            return encoded_str
        else:
            return encoded_str.decode()

    def _decode_jwt(self, encoded: str) -> Optional[dict]:
        """JWT decode data - relies on PyJWT.

        Args:
            encoded (str): Encoded string that is to be decoded

        Returns:
            dict: Dictionary of the decoded token or None if there is an error
                  during the decoding process.

        """
        secret = cast(str, self._secret)
        try:
            return jwt.decode(encoded, secret, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return None

    def _split_redirect_url(self, redirect_url):
        """Splits the redirect URL to extract code and state parameters.

        Used for the initial token request.

            Args:
                redirect_url (str): The redirect URL to be split

            Returns:
                dict: code and state values in a dictionary
        """
        code_pattern = "code=(.*)&"
        match = re.search(code_pattern, redirect_url)
        if match:
            code = {"code": match.group(1)}
        else:
            return None

        state_pattern = "state=(.*)$"
        match = re.search(state_pattern, redirect_url)
        if match:
            state = self._decode_jwt(match.group(1))

        return {**code, **state}

    async def _async_refresh_token(self, token: dict) -> dict:
        """Refresh the access token.

        Args:
            token (dict): Token to be updated

        Returns:
            dict: Token dictionary with the new access token and
            expiration times
        """
        new_token = await self._token_request(
            {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "refresh_token": token["refresh_token"],
            }
        )
        return {**token, **new_token}

    async def _token_request(self, data: dict) -> dict:
        """Make an HTTP POST request for a token.

        This method will call the token updater method if it exists.

        Arg:
            data (dict): Dictionary of the POST body parameters

        Returns:
            dict: Token dictionary returned by the API

        Raises:
            HTTP status error exceptions
        """
        data["client_id"] = self.client_id

        if self.client_secret is not None:
            data["client_secret"] = self.client_secret

        resp = await self.oauth_client.post(
            HomePlusOAuth2Async.TOKEN_URL, data=data
        )
        resp.raise_for_status()

        self.token = cast(dict, await resp.json())
        if self.token_updater is not None:
            await self.token_updater(self.token)
        return self.token

    def generate_authorize_url(self) -> str:
        """Generate the URL for the user to authorize the app.

        Returns:
            str: The URL that is used for the authorization step.

        """
        return str(
            URL(HomePlusOAuth2Async.AUTH_BASE_URL).with_query(
                {
                    "response_type": "code",
                    "client_id": self.client_id,
                    "redirect_uri": self.redirect_uri,
                    "state": self._encode_jwt({"state": self._state}),
                }
            )
        )

    async def async_ensure_token_valid(self) -> str:
        """Ensures that the access token is valid.

        *Deprecated* - Use `async_get_access_token()` instead.

        Returns:
            str: String containing the new access token. The object attribute
                 that holds the token is also updated.
        """
        return await self.async_get_access_token()

    async def async_get_access_token(self) -> str:
        """Return a valid access token.

        If the current token is no longer valid, then a new one is requested
        and the object attribute updated.
        If the current token is still valid, then do nothing.

        Returns:
            str: String containing the new access token. The object attribute
                 that holds the token is also updated.
        """
        if self.valid_token:
            self.logger.debug("Token is still valid")
            return self.token
        self.logger.debug("Token is no longer valid so refreshing")
        return await self._async_refresh_token(self.token)

    async def async_fetch_initial_token(self, redirect_url: Any) -> dict:
        """Fetches the initial access and refresh tokens once the
        authorization step was completed.

        This method relies on the redirect URL that was provided by the
        API once authorization was approved.

        Args:
            redirect_url (str): The redirect URL that was provided by
                                the API after authorizing.

        Returns:
            dict: Dictionary of the new token. The object attribute that
                  holds the token is also updated.

        """
        req_body = self._split_redirect_url(redirect_url)

        if req_body is not None and req_body["state"] == self._state:
            return await self._token_request(
                {
                    "grant_type": "authorization_code",
                    "code": req_body["code"],
                }
            )
