"""
Copyright (c) 2021 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.


Wrapper interface for the REST API to grafana
"""

import json
import logging
from dataclasses import dataclass
from typing import Dict

import sys
import requests
import six

logger = logging.getLogger()
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class TokenAuth(requests.auth.AuthBase):
    """
    Authentication using a Grafana API token.
    """

    def __init__(self, token: str):
        self.token = token

    def __call__(self, request: requests.models.Request):
        request.headers.update({
            "Authorization": f"Bearer {self.token}"
        })
        return request


class RestApiBasicAuth:
    """
    HTTP REST calls with status code checking and common auth/headers
    """

    def __init__(self, host: str = "", credentials=None) -> None:
        self.host = host
        self.session = requests.Session()
        self.session.headers = {
            "Accept": "application/json; charset=UTF-8"
        }
        if credentials is None:
            pass
        elif isinstance(credentials, six.string_types):
            self.session.auth = TokenAuth(credentials)
            self.isTokenAuth  = True
        else:
            self.session.auth = requests.auth.HTTPBasicAuth(*credentials)
            self.isTokenAuth  = False

    def get(self, resource: str) -> Dict:
        """HTTP GET"""
        response = self.session.request("GET", f"{self.host}/api/{resource}")
        return self._check_response(response.status_code, json.loads(response.text))

    def post(self, resource: str, body: dict) -> Dict:
        """HTTP POST"""
        response = self.session.request(
            "POST",
            f"{self.host}/api/{resource}",
            json=body
        )
        return self._check_response(response.status_code, json.loads(response.text))

    def put(self, resource: str, body: dict) -> Dict:
        """HTTP PUT"""
        response = self.session.request(
            "PUT",
            f"{self.host}/api/{resource}",
            json=body
        )
        return self._check_response(response.status_code, json.loads(response.text))

    def delete(self, resource: str) -> Dict:
        """HTTP DELETE"""
        response = self.session.request("DELETE", f"{self.host}/api/{resource}")
        return self._check_response(response.status_code, json.loads(response.text))

    @staticmethod
    def _check_response(status, response) -> Dict:
        """Gives just the response body if response is ok, otherwise fail hard"""
        if status != 200:
            message = response["message"]
            print(f"Request failed - 'HTTP error {status}: {message}'", file=sys.stderr)
            quit(1)

        return response


@dataclass
class GrafanaAPI:
    """Container for API config and the api access interface"""

    host: str = ""
    credentials = None
    api: RestApiBasicAuth = RestApiBasicAuth()


# Other modules import this config object to access 'global' args
grafana = GrafanaAPI()
