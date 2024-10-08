from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import requests

from .OMFError import OMFError


class Authentication(object):
    def __init__(self, tenant: str, url: str, client_id: str, client_secret: str):
        self.__tenant = tenant
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__url = url

        self.__expiration = 0
        self.__token = ''
        if client_secret is not None:
            self.__getToken = self.__getClientIDSecretToken
        else:
            self.__getToken = self.__getPKCEToken

    def getToken(self) -> str:
        if (self.__expiration - time.time()) > 5 * 60:
            return self.__token

        return self.__getToken()

    def __getClientIDSecretToken(self) -> str:
        # Get OAuth endpoint configuration
        endpoint = json.loads(
            requests.get(
                self.__url + '/identity/.well-known/openid-configuration'
            ).content
        )
        token_endpoint = endpoint.get('token_endpoint')

        tokenInformation = requests.post(
            token_endpoint,
            data={
                'client_id': self.__client_id,
                'client_secret': self.__client_secret,
                'grant_type': 'client_credentials',
            },
        )

        token = json.loads(tokenInformation.content)

        expiration = token.get('expires_in', None)
        if expiration is None:
            raise OMFError(
                f'Failed to get token, check client id/secret: {token["error"]}'
            )

        self.__expiration = float(expiration) + time.time()
        self.__token = token['access_token']
        return self.__token

    def __getPKCEToken(self) -> str:
        try:
            redirect_uri = 'http://localhost:5004/callback.html'
            scope = 'openid ocsapi'

            # Set up PKCE Verifier and Code Challenge
            verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=')
            challenge = base64.urlsafe_b64encode(
                hashlib.sha256(verifier).digest()
            ).rstrip(b'=')

            # Get OAuth endpoint configuration
            print('Step 1: Get OAuth endpoint configuration...')
            endpoint = json.loads(
                requests.get(
                    self.__url + '/identity/.well-known/openid-configuration'
                ).content
            )
            auth_endpoint = endpoint.get('authorization_endpoint')
            token_endpoint = endpoint.get('token_endpoint')

            # Set up request handler for web browser login
            print('Step 2: Set up server to process authorization response...')

            class RequestHandler(BaseHTTPRequestHandler):
                """Handles authentication redirect uri and extracts authorization code from URL"""

                code = ''

                def do_GET(self):
                    """Handles GET request against this temporary local server"""
                    # Parse out authorization code from query string in request
                    RequestHandler.code = parse_qs(urlparse(self.path).query)['code'][0]

                    # Write response
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write(
                        '<h1>You can now return to the application.</h1>'.encode()
                    )

            # Set up server for web browser login
            server = HTTPServer(('', 5004), RequestHandler)

            # Open web browser against authorization endpoint
            print('Step 3: Authorize the user...')
            auth_url = (
                auth_endpoint
                + '?response_type=code&code_challenge='
                + challenge.decode()
                + '&code_challenge_method=S256&client_id='
                + self.__client_id
                + '&redirect_uri='
                + redirect_uri
                + '&scope='
                + scope
                + '&acr_values=tenant:'
                + self.__tenant
            )

            # Open user default web browser at Auth page
            if not webbrowser.open(auth_url):
                raise OMFError(
                    'This notebook/script should be run locally on your machine to authenticate'
                )

            # Wait for response in browser
            print('Step 4: Set server to handle one request...')
            server.handle_request()

            # Use authorization code to get bearer token
            print('Step 5: Get a token using the authorization code...')
            token = requests.post(
                token_endpoint,
                [
                    ('grant_type', 'authorization_code'),
                    ('client_id', self.__client_id),
                    ('code_verifier', verifier),
                    ('code', RequestHandler.code),
                    ('redirect_uri', redirect_uri),
                ],
            )

            token = json.loads(token.content)
            expiration = token.get('expires_in', None)
            if expiration is None:
                raise OMFError(
                    f'Failed to get token, please retry login in: {token["error"]}'
                )

            self.__expiration = float(expiration) + time.time()
            self.__token = token['access_token']
            print(f'Step 6: Access token read ok\nComplete!')
            return self.__token

        except Exception as error:
            msg = 'Encountered Error: {error}'.format(error=error)
            raise OMFError(msg)
