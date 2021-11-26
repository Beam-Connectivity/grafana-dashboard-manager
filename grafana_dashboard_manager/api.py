"""
Copyright (c) 2021 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.


Wrapper interface for the REST API to grafana
"""

import json
import logging
import sys
from dataclasses import dataclass
from typing import Dict

import requests

logger = logging.getLogger()
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class RestApiBasicAuth:
    """
    HTTP REST calls with status code checking and common auth/headers
    """

    def __init__(self, host: str = "", username: str = "", password: str = "") -> None:
        self.host = host
        self.username = username
        self.password = password

    def get(self, resource: str) -> Dict:
        """HTTP GET"""
        response = requests.get(f"{self.host}/api/{resource}", auth=(self.username, self.password))
        return self._check_response(response.status_code, json.loads(response.text))

    def post(self, resource: str, body: dict) -> Dict:
        """HTTP POST"""
        response = requests.post(
            f"{self.host}/api/{resource}",
            auth=(self.username, self.password),
            json=body,
            headers={"Content-type": "application/json"},
        )
        return self._check_response(response.status_code, json.loads(response.text))

    def put(self, resource: str, body: dict) -> Dict:
        """HTTP PUT"""
        response = requests.put(f"{self.host}/api/{resource}", auth=(self.username, self.password), data=body)
        return self._check_response(response.status_code, json.loads(response.text))

    def delete(self, resource: str) -> Dict:
        """HTTP DELETE"""
        response = requests.delete(f"{self.host}/api/{resource}", auth=(self.username, self.password))
        return self._check_response(response.status_code, json.loads(response.text))

    @staticmethod
    def _check_response(status, response) -> Dict:
        """Gives just the response body if response is ok, otherwise fail hard"""
        if status != 200:
            raise requests.HTTPError(f"{status}: {response}")

        return response


@dataclass
class GrafanaAPI:
    """Container for API config and the api access interface"""

    host: str = ""
    username: str = ""
    password: str = ""
    api: RestApiBasicAuth = RestApiBasicAuth()


# Other modules import this config object to access 'global' args
grafana = GrafanaAPI()
