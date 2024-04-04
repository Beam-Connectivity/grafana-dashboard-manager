"""
Copyright (c) 2024 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

import logging

from grafana_dashboard_manager.api.auth import GrafanaAuth, GrafanaAuthType
from grafana_dashboard_manager.api.rest_client import RestClient
from grafana_dashboard_manager.handlers.api_dashboards import ApiDashboards
from grafana_dashboard_manager.handlers.api_folders import ApiFolders

logger = logging.getLogger()


class GrafanaApi:
    """HTTP REST calls with status code checking and common auth/headers"""

    CLIENT_HEADERS = {
        "Accept": "application/json; charset=UTF-8",
        "Content-Type": "application/json",
    }

    def __init__(
        self,
        scheme: str,
        host: str,
        port: int,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        org: int | None = None,
        skip_verify: bool = False,
        verbose: bool = False,
    ) -> None:
        """Wrapper object to interact with Grafana entities like Folders and Dashboards via the HTTP API"""
        self.host = f"{scheme}://{host}:{port}"

        # Set the X-Grafana-Org-Id header if this request is for a given organization
        if org:
            self.CLIENT_HEADERS.update({"X-Grafana-Org-Id": str(org)})

        self._api = RestClient(
            self.CLIENT_HEADERS,
            self._init_auth(token, username, password),
            f"{self.host}/api/",
            skip_verify,
            verbose,
        )

        self.folders = ApiFolders(self._api)
        self.dashboards = ApiDashboards(self._api)

    def _init_auth(self, token, username, password):
        if token:
            logger.info("Using Bearer token header auth")
            auth = GrafanaAuth(GrafanaAuthType.BEARER, token=token)
        elif username and password:
            logger.info(f"Using Basic auth with user '{username}'")
            auth = GrafanaAuth(GrafanaAuthType.BASIC, username=username, password=password)
        else:
            raise ValueError("Supply either a bearer token or username/password for basic auth")

        return auth
