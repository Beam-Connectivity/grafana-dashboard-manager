"""
Copyright (c) 2024 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

import json
import logging
import os

from grafana_dashboard_manager.global_config import GlobalConfig
from grafana_dashboard_manager.grafana.grafana_api import GrafanaApi
from grafana_dashboard_manager.models import DashboardFolderLookup, DashboardSearchResult
from grafana_dashboard_manager.utils import confirm, show_dashboard_folders

logger = logging.getLogger(__name__)


def download_dashboards(config: GlobalConfig, client: GrafanaApi):
    """Download folder-structured dashboards and write to json files at the destination_root path"""
    destination_dir = config.destination
    if destination_dir is None:
        raise ValueError("No destination directory set")

    # Check destination folder is empty
    dest_contents = os.listdir(destination_dir)
    destination_is_empty = len(dest_contents) == 0 or (len(dest_contents) == 1 and ".DS_Store" in dest_contents)

    if config.non_interactive or config.overwrite and not destination_is_empty:
        logger.warning(f"Potentially overwriting files in {destination_dir}")
    if not destination_is_empty and not config.non_interactive:
        confirm("Destination directory is not empty. Confirm overwrite?")

    logger.info(f"Pulling all dashboards into {destination_dir}...")

    # Get the folders to replicate locally in the destination_dir
    folders = client.folders.all_folders()

    # Keeps track of folders and the dashboards they contain
    folder_dashboards: dict[str, DashboardFolderLookup] = {
        folder.title: DashboardFolderLookup(id=folder.id, uid=folder.uid, title=folder.title) for folder in folders
    }
    logger.info(f"Grafana folders found: {', '.join(folder_dashboards.keys())}")

    # Iterate over each folder and grab the dashboards
    for folder_title, folder in folder_dashboards.items():
        dashboards = client.folders.dashboards_in_folder(folder.id)
        folder_dashboards[folder_title].dashboards.extend(
            [DashboardSearchResult.model_validate(dashboard) for dashboard in dashboards]
        )

    show_dashboard_folders(folder_dashboards)
    if not config.non_interactive:
        confirm(f"Download these dashboard jsons files to '{destination_dir}'?")

    for folder_title, folder in folder_dashboards.items():
        for dashboard in folder.dashboards:
            escaped_dashboard_title = dashboard.title.replace("/", "-").replace("\\", "-").replace(" ", "_")
            dest_file_path = destination_dir / folder_title / f"{escaped_dashboard_title}.json"
            client.dashboards.save(dashboard.uid, dest_file_path)
        logger.info(f"Saved {len(folder.dashboards)} dashboards to {destination_dir / folder_title}")

    # Home
    client.dashboards.save_home(destination_dir)

    # Store folder information in a folders.json file for use when re-creating folders, we can ensure they have the same
    # folderUid
    with (destination_dir / "folders.json").open("w") as file:
        data = {key: value.model_dump() for key, value in folder_dashboards.items()}
        file.write(json.dumps(data, indent=2))
