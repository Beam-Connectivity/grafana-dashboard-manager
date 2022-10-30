"""
Copyright (c) 2021 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.


Contains CLI commands for Grafana dashboards

Folders use id instead of uid https://github.com/grafana/grafana/discussions/37016
So when dashboards are downloaded/uploaded the IDs need to be dynamically updated as they are different per
deployment database
"""


import json
import logging
import urllib.parse
from typing import Dict, List

import rich
import typer

from .api import grafana

app = typer.Typer()
logger = logging.getLogger()

ARG_UID = typer.Argument(..., help="The unique identifier for the dashboard")
ARG_TITLE = typer.Argument(..., help="The display title for the dashboard")
BASE_RESOURCE = "dashboards"


@app.command()
def get(dashboard: str = ARG_UID):
    """
    Get the JSON definition for an existing dashboard by uid.
    """
    response = grafana.api.get(f"{BASE_RESOURCE}/uid/{dashboard}")
    rich.print_json(json.dumps(response))


@app.command()
def show():
    """
    Show all the dashboards by uid
    """
    rich.print(_get_all_dashboard_uids())


def update_dashlist_folder_ids(dashboard_definition: Dict) -> Dict:
    """
    Checks consistency between the id of folders in the database with the dashlist panel definitions,
    updating if necessary.
    """

    # Some dashboards use a list of "rows" with "panels" nested within, some dashboards just use "panels".
    # If using "rows", we need to iterate over "rows" to extract all of the "panels"
    if "panels" in dashboard_definition["dashboard"]:
        for panel in dashboard_definition["dashboard"]["panels"]:
            panel = update_single_dashlist_folder_id(panel)
    elif "rows" in dashboard_definition["dashboard"]:
        for row in dashboard_definition["dashboard"]["rows"]:
            for panel in row["panels"]:
                panel = update_single_dashlist_folder_id(panel)
    else:
        title = dashboard_definition["dashboard"]["title"]
        logger.exception(f"❌ {title} does not have any any panels")

    return dashboard_definition


def update_single_dashlist_folder_id(panels_definition: Dict) -> Dict:
    if panels_definition["type"] == "dashlist":
        # Look up the target folder using the panel title - it needs to match!
        folder_name = panels_definition["title"]
        logger.info(f"Searching for folders with name {folder_name}")

        # There can only be one folder with this name
        response = grafana.api.get(
            f"search?query={urllib.parse.quote(folder_name)}&type=dash-folder")

        # If there's no folder, it could be referencing other things like recent dashboards, alerts etc
        if not response:
            return panels_definition

        folder_id = response[0]["id"]
        logger.info(f"{folder_name} folder has ID {folder_id}")

        # Ensure that the folder id in the dashboard definition matches
        if panels_definition["options"]["folderId"] == folder_id:
            logger.info(
                f"Panel folderId option already correct: {folder_id}")
        else:
            logger.info(f"Updating panel folderId option to {folder_id}")
            panels_definition["options"]["folderId"] = folder_id
    return panels_definition


def _get_all_dashboard_uids() -> List[str]:
    response = grafana.api.get("search?query=%")
    return [db["uid"] for db in response]
