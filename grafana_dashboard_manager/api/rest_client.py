"""
Copyright (c) 2024 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

import logging

import httpx

logger = logging.getLogger(__name__)


class RestClient:
    """Provides RESTful calls"""

    def __init__(self, headers, auth, base_url, skip_verify, verbose):
        """
        Wrapper on the httpx client to centralise request level exception handling

        Args:
            headers: common headers to apply to all requests
            auth: an httpx auth object
            base_url: url host
            skip_verify: set to true to skip verification of https connection certs
            verbose: increased logging output

        """
        self.client = httpx.Client(headers=headers, auth=auth, base_url=base_url, verify=skip_verify)
        self.verbose = verbose

    def get(self, resource: str) -> httpx.Response:
        """HTTP GET"""
        return self._make_request("GET", resource)

    def post(self, resource: str, body: dict | None = None) -> httpx.Response:
        """HTTP POST"""
        return self._make_request("POST", resource, body)

    def put(self, resource: str, body: dict) -> httpx.Response:
        """HTTP PUT"""
        return self._make_request("PUT", resource, body)

    def patch(self, resource: str, body: dict) -> httpx.Response:
        """HTTP PATCH"""
        return self._make_request("PATCH", resource, body)

    def delete(self, resource: str) -> httpx.Response:
        """HTTP DELETE"""
        return self._make_request("DELETE", resource)

    def _make_request(self, verb: str, resource: str, body: dict | None = None) -> httpx.Response:
        # Handle connection errors
        try:
            response = self.client.request(verb, resource, json=body)
        except Exception as exc:
            if self.verbose:
                raise
            logger.error(f"Could not connect to {self.client.base_url}{resource}")
            logger.error(exc)
            exit(1)

        return response
