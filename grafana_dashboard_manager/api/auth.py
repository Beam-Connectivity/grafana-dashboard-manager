"""
Copyright (c) 2024 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

from base64 import b64encode
from enum import Enum

import httpx


class GrafanaAuthType(Enum):
    """Defines the supported authentication methods"""

    BASIC = "Basic"
    BEARER = "Bearer"


class GrafanaAuth(httpx.Auth):
    """Configures Grafana auth for use with httpx auth"""

    def __init__(
        self,
        auth_type: GrafanaAuthType,
        *,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
    ):
        """
        Creates an auth object which either supports basic auth with username/password, or a bearer token

        Args:
            auth_type: enum for auth scheme
            username: basic auth username (default: {None})
            password: basic auth password (default: {None})
            token: bearer token auth token (default: {None})

        Returns:
            None

        Raises:
            ValueError: if provided args does not satisfy the requirements of auth_type

        """
        self.auth_type = auth_type
        self.auth_header_prefix = auth_type.value

        self.username = username
        self.password = password
        self.token = token
        self._credential = None

        match auth_type:
            case GrafanaAuthType.BASIC:
                if not self.username and self.password:
                    raise ValueError("Must provide username and password when using Basic Auth")
                self._credential = b64encode(f"{self.username}:{self.password}".encode()).decode()

            case GrafanaAuthType.BEARER:
                if not self.token:
                    raise ValueError("Must provide token when using Token Auth")
                self._credential = self.token

            case _:
                raise ValueError(f"Unsupported auth type: {auth_type}")

    def auth_flow(self, request):
        """Required override: https://www.python-httpx.org/advanced/#customizing-authentication"""
        request.headers["Authorization"] = f"{self.auth_header_prefix} {self._credential}"
        yield request
