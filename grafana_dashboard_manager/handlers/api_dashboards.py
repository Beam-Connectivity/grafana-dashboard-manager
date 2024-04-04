"""
Copyright (c) 2024 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import httpx

from grafana_dashboard_manager.api.rest_client import RestClient
from grafana_dashboard_manager.exceptions import GrafanaApiException
from grafana_dashboard_manager.handlers.base_handler import BaseHandler
from grafana_dashboard_manager.models import DashboardResponse

logger = logging.getLogger(__name__)


class ApiDashboards(BaseHandler):
    """Handler class to interact with Dashboards via API"""

    model = DashboardResponse

    def __init__(self, api: RestClient):
        """Provide a RestClient to use for API calls"""
        self.api = api

    def by_id(self, id: int) -> DashboardResponse:
        """Get a dashboard with a dashboard ID int"""
        response = self.api.get(f"dashboards/id/{id}")
        return self._response_to_model(response)

    def by_uid(self, uid: str) -> DashboardResponse:
        """Get a dashboard with a dashboard UID string"""
        response = self.api.get(f"dashboards/uid/{uid}")
        return self._response_to_model(response)

    def save(self, uid: str, file: Path) -> None:
        """Download a dashboard to a local path"""
        file.parent.mkdir(parents=True, exist_ok=True)

        dashboard = self.api.get(f"dashboards/uid/{uid}").json()["dashboard"]
        self._write_json(dashboard, file)

    def save_home(self, directory: Path) -> None:
        """Download the home dashboard"""
        dest_file = directory / "home.json"
        response = self.api.get("dashboards/home").json()

        # If the dashboard has been set to a custom dashboard, the response will be a direct to that dashboard
        if "redirectUri" in response:
            home_uid = response["redirectUri"].split("/")[2]
            logger.info(f"Custom home dashboard has been set: {home_uid=} and saved to {dest_file}")
            dashboard = self.api.get(f"dashboards/uid/{home_uid}").json()["dashboard"]
        else:
            dashboard = response["dashboard"]

        self._write_json(dashboard, dest_file)

    def create(self, dashboard: dict, folder_uid: str | None = None, overwrite: bool = True) -> None:
        """Create a new dashboard"""
        dashboard.pop("id", None)

        if not folder_uid:
            logger.warning(f"Dashboard {dashboard['title']} has no folder and will be added at the root level")
        payload = {
            "dashboard": dashboard,
            "folderUid": folder_uid,
            "message": f"Uploaded at {datetime.now()}",
            "overwrite": overwrite,
        }

        response = self.api.post("dashboards/db", body=payload)

        if response.status_code != 200:
            logger.error(f"Failed to upload {dashboard['title']} - {response.json()}")

    def create_home(self, dashboard: dict) -> str:
        """Create the home dashboard (store in the default General folder by convention)"""
        dashboard.pop("id", None)

        response = self.api.post(
            "dashboards/db",
            body={
                "dashboard": dashboard,
                "folderId": 0,
                "message": f"Uploaded at {datetime.now()}",
                "overwrite": True,
            },
        )

        if response.status_code != 200:
            raise GrafanaApiException(
                f"{response.status_code}: Failed to upload {dashboard['title']} - {response.json()}"
            )

        return response.json()["uid"]

    def set_home(self, uid: str) -> None:
        """Set a given dashboard as the default home dashboard for the current organization"""
        response = self.api.patch("/org/preferences", {"homeDashboardUID": uid})
        if response.status_code != 200:
            raise GrafanaApiException(f"Failed to set home dashboard {response.json()}")

    def _write_json(self, data: dict, path: Path):
        with path.open("w") as f:
            f.write(json.dumps(data, indent=4))

    def _response_to_model(self, response: httpx.Response):
        body = response.json()
        folder = self.model.model_validate(body)
        return folder
