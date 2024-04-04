"""
Copyright (c) 2024 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

import logging
from typing import Type

from grafana_dashboard_manager.api.rest_client import RestClient
from grafana_dashboard_manager.exceptions import FolderExistsException, FolderNotFoundException, GrafanaApiException
from grafana_dashboard_manager.handlers.base_handler import BaseHandler
from grafana_dashboard_manager.models import DashboardSearchResult, Folder

logger = logging.getLogger(__name__)


class ApiFolders(BaseHandler[Folder]):
    """Handler class to interact with Folders via API"""

    model: Type[Folder] = Folder

    def __init__(self, api: RestClient):
        """Provide a RestClient to use for API calls"""
        self.api = api

    def all_folders(self) -> list[Folder]:
        """Get a list of all folders"""
        response = self.api.get("folders")
        body = response.json()
        return [Folder.model_validate(folder) for folder in body]

    def dashboards_in_folder(self, folder_id: int) -> list[DashboardSearchResult]:
        """Get a list of all dashboards within a given folder"""
        response = self.api.get(f"search?folderIds={folder_id}")
        body = response.json()
        return [DashboardSearchResult.model_validate(dashboard) for dashboard in body]

    def general_folder(self) -> Folder:
        """Get details for the default General folder"""
        return self.by_id(0)

    def by_uid(self, uid: str) -> Folder:
        """Get folder details by its folderUid"""
        response = self.api.get(f"folders/uid/{uid}")
        return self.response_to_model(response)

    def by_id(self, id: int) -> Folder:
        """Get folder details by its folderId"""
        response = self.api.get(f"folders/id/{id}")
        return self.response_to_model(response)

    def by_name(self, name: str) -> Folder:
        """Get folder details by its name (title)"""
        response = self.api.get(f"search?type=dash-folder&query={name}")
        try:
            return self.model.model_validate(response.json()[0])
        except IndexError as exc:
            raise FolderNotFoundException(f"No results for folder with {name=}") from exc

    def create(self, title: str, uid: str | None = None, *, overwrite: bool = True) -> Folder:
        """Create a new dashboard"""
        body = {
            "uid": uid,
            "title": title,
        }
        response = self.api.post("folders", body)

        if response.status_code not in {200, 409, 412}:
            raise GrafanaApiException(f"Could not update folder '{title}': {response.json()}")

        else:
            if response.status_code == 200:
                response_uid = response.json().get("uid")
                logger.info(f"Created folder with title '{title}' with uid={response_uid}")
                return self.response_to_model(response)

            # Retry with PUT (i.e. update)
            if overwrite is False:
                raise FolderExistsException(f"Folder already exists: {title=} {uid=}. Use overwrite option")

            response = self.api.put(f"folders/{uid}", {**body, "overwrite": True})
            if response.status_code == 200:
                response_uid = response.json().get("uid")
                logger.info(f"Updated folder title to '{title}' (uid={response_uid})")
                return self.response_to_model(response)
            else:
                raise GrafanaApiException(f"Could not update folder '{title}': {response.json()}")
