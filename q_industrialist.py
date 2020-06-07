""" Q.Industrialist (desktop/mobile)

Prerequisites:
    * Create an SSO application at developers.eveonline.com with the scope
      "esi-characters.read_blueprints.v1" and the callback URL
      "https://localhost/callback/". Note: never use localhost as a callback
      in released applications.
    * Have a Python 3 environment available to you (possibly by using a
      virtual environment: https://virtualenv.pypa.io/en/stable/).
    * Run pip install -r requirements.txt with this directory as your root.

To run this example, make sure you have completed the prerequisites and then
run the following command from this directory as the root:

>>> python q_industrialist.py
"""
import base64
import hashlib
import secrets
import sys
import json

from shared_flow import print_auth_url
from shared_flow import send_token_request
from shared_flow import send_token_refresh
from shared_flow import handle_sso_token_response
from shared_flow import send_esi_request
from auth_cache import read_cache
from auth_cache import make_cache
from auth_cache import store_cache
from auth_cache import is_timestamp_expired
from auth_cache import get_timestamp_expired

import q_industrialist_settings


# R Initiative 4 Q.Industrialist
g_ri4_client_id = "022ea197e3f2414f913b789e016990c8"
g_client_scope = ["esi-characters.read_blueprints.v1",
                  "esi-wallet.read_character_wallet.v1"]


def print_sso_failure(sso_response):
    print("\nSomething went wrong! Here's some debug info to help you out:")
    print("\nSent request with url: {} \nbody: {} \nheaders: {}".format(
        sso_response.request.url,
        sso_response.request.body,
        sso_response.request.headers
    ))
    print("\nSSO response code is: {}".format(sso_response.status_code))
    print("\nSSO response JSON is: {}".format(sso_response.json()))


def auth():
    print("Follow the prompts and enter the info asked for.")

    # Generate the PKCE code challenge
    random = base64.urlsafe_b64encode(secrets.token_bytes(32))
    m = hashlib.sha256()
    m.update(random)
    d = m.digest()
    code_challenge = base64.urlsafe_b64encode(d).decode().replace("=", "")

    client_id = input("Copy your SSO application's client ID and enter it "
                      "here [press 'Enter' for R Initiative 4 app]: ")
    if not client_id:
        global g_ri4_client_id
        client_id = g_ri4_client_id

    # Because this is a desktop/mobile application, you should use
    # the PKCE protocol when contacting the EVE SSO. In this case, that
    # means sending a base 64 encoded sha256 hashed 32 byte string
    # called a code challenge. This 32 byte string should be ephemeral
    # and never stored anywhere. The code challenge string generated for
    # this program is ${random} and the hashed code challenge is ${code_challenge}.
    # Notice that the query parameter of the following URL will contain this
    # code challenge.

    global g_client_scope
    print_auth_url(client_id, g_client_scope, code_challenge=code_challenge)

    auth_code = input("Copy the \"code\" query parameter and enter it here: ")

    code_verifier = random

    form_values = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": auth_code,
        "code_verifier": code_verifier
    }

    # Because this is using PCKE protocol, your application never has
    # to share its secret key with the SSO. Instead, this next request
    # will send the base 64 encoded unhashed value of the code
    # challenge, called the code verifier, in the request body so EVE's
    # SSO knows your application was not tampered with since the start
    # of this process. The code verifier generated for this program is
    # ${code_verifier} derived from the raw string ${random}

    sso_auth_response = send_token_request(form_values)

    if sso_auth_response.status_code == 200:
        data = sso_auth_response.json()
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        auth_cache = make_cache(access_token, refresh_token)
        return auth_cache
    else:
        print_sso_failure(sso_auth_response)
        sys.exit(1)

    # handle_sso_token_response(sso_auth_response)


def re_auth(auth_cache):
    refresh_token = auth_cache["refresh_token"]
    client_id = auth_cache["client_id"]

    sso_auth_response = send_token_refresh(refresh_token, client_id)

    if sso_auth_response.status_code == 200:
        data = sso_auth_response.json()

        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        expired = get_timestamp_expired(int(data["expires_in"]))

        auth_cache.update({"access_token": access_token})
        auth_cache.update({"refresh_token": refresh_token})
        auth_cache.update({"expired": expired})
        store_cache(auth_cache)
        return auth_cache
    else:
        print_sso_failure(sso_auth_response)
        sys.exit(1)


def main():
    cache = read_cache()
    if not ('access_token' in cache) or not ('refresh_token' in cache) or (not 'expired' in cache):
        cache = auth()
    elif is_timestamp_expired(int(cache["expired"])):
        cache = re_auth(cache)

    access_token = cache["access_token"]
    character_id = cache["character_id"]
    character_name = cache["character_name"]

    blueprint_path = ("https://esi.evetech.net/latest/characters/{}/blueprints/".format(character_id))
    blueprint_data = send_esi_request(access_token, blueprint_path)
    print("\n{} has {} blueprints".format(character_name, len(blueprint_data)))
    # print("{}".format(json.dumps(blueprint_data, indent=1, sort_keys=False)))

    wallet_path = ("https://esi.evetech.net/latest/characters/{}/wallet/".format(character_id))
    wallet_data = send_esi_request(access_token, wallet_path)
    print("\n{} has {} ISK".format(character_name, wallet_data))


if __name__ == "__main__":
    main()
