import asyncio
import time

from homepluscontrol import authentication

client_id = "client_identifier"
client_secret = "client_secret"
subscription_key = "subscription_key"
redirect_uri = "https://www.dummy.com:1123/auth"


def test_token_validity():
    async def test_coroutine():
        token = {
            "access_token": "AcCeSs_ToKeN",
            "refresh_token": "ReFrEsH_ToKeN",
            "expires_in": -1,
            "expires_on": time.time() - 1,
        }
        # Test for expired token
        client = authentication.HomePlusOAuth2Async(
            client_id=client_id,
            client_secret=client_secret,
            subscription_key=subscription_key,
            redirect_uri=redirect_uri,
            token=token,
        )
        assert not client.valid_token

        # Test for valid token
        token["expires_on"] = time.time() + 500
        client.token = token
        assert client.valid_token

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_coroutine())


def test_generation_auth_url():
    async def test_coroutine():
        token = {
            "access_token": "AcCeSs_ToKeN",
            "refresh_token": "ReFrEsH_ToKeN",
            "expires_in": -1,
            "expires_on": time.time() + 500,
        }
        # Test for expired token
        client = authentication.HomePlusOAuth2Async(
            client_id=client_id,
            client_secret=client_secret,
            subscription_key=subscription_key,
            redirect_uri=redirect_uri,
            token=token,
        )
        expected_url = "https://partners-login.eliotbylegrand.com/authorize?response_type=code&client_id=client_identifier&redirect_uri=https://www.dummy.com:1123/auth&state="
        assert client.generate_authorize_url().startswith(expected_url)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_coroutine())


def test_split_redirect_url():
    async def test_coroutine():
        token = {
            "access_token": "AcCeSs_ToKeN",
            "refresh_token": "ReFrEsH_ToKeN",
            "expires_in": -1,
            "expires_on": time.time() + 500,
        }
        # Test for expired token
        client = authentication.HomePlusOAuth2Async(
            client_id=client_id,
            client_secret=client_secret,
            subscription_key=subscription_key,
            redirect_uri=redirect_uri,
            token=token,
        )
        expected_state = client._encode_jwt({"state": "expected_state"})
        expected_url = f"http://www.dummy.com:1123/auth?code=expected_code&state={expected_state}"
        result = client._split_redirect_url(expected_url)

        assert result["code"] == "expected_code"
        assert result["state"] == "expected_state"

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_coroutine())


def test_decode_state():
    async def test_coroutine():
        token = {
            "access_token": "AcCeSs_ToKeN",
            "refresh_token": "ReFrEsH_ToKeN",
            "expires_in": -1,
            "expires_on": time.time() + 500,
        }
        # Test for expired token
        client = authentication.HomePlusOAuth2Async(
            client_id=client_id,
            client_secret=client_secret,
            subscription_key=subscription_key,
            redirect_uri=redirect_uri,
            token=token,
        )
        # Test valid encode/decode
        expected_state = client._encode_jwt({"state": "expected_state"})
        result = client._decode_jwt(expected_state)
        assert result["state"] == "expected_state"

        # Test invalid decode
        result = client._decode_jwt(2)
        assert result is None

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_coroutine())
