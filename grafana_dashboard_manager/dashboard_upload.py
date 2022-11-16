"""
Copyright (c) 2021 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.


Upload dashboards from json files to a Grafana web instance
"""

import json
import logging
from pathlib import Path
import importlib.metadata

import rich
import typer
from rich.tree import Tree
from requests import HTTPError

from .api import grafana
from .dashboard import update_dashlist_folder_ids
from .tree import walk_directory

app = typer.Typer()
logger = logging.getLogger()

VERSION = importlib.metadata.version('grafana-dashboard-manager')


@app.command()
def all(
    source_dir: Path = typer.Option(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=True,
    )
):  # pylint: disable=redefined-builtin
    """
    Download folder-structured dashboards and write to json files at the destination_root path
    """
    logger.info(f"Pushing all dashboards from {source_dir}...")
    tree = Tree(
        f":open_file_folder: [link file://{source_dir}]{source_dir}",
        guide_style="bold bright_blue",
    )
    rich.print(walk_directory(source_dir, tree))

    for folder in source_dir.glob("*"):
        if folder.is_dir():
            for dashboard_file in folder.glob("*.json"):
                if folder.name == "General":
                    folder_uid = "general"
                else:
                    folder_uid = create_update_folder(folder.name)

                create_update_dashboard(dashboard_file, folder_uid)

    # Set home dashboard
    set_home_dashboard()
    logger.info("✅")


def create_update_folder(title: str) -> str:
    """
    Create a folder with a given title if it doesn't exist
    """
    for _folder in grafana.api.get("folders"):
        if _folder["title"] == title:
            return _folder["uid"]

    # The uid is the title but lowered snake case
    request = {"uid": title.lower().replace(" ", ""), "title": title}
    logger.info(f"Creating folder {title}..")
    response = grafana.api.post("folders", request)
    return response["uid"]


def create_update_dashboard(dashboard_file: Path, folder_uid: str):
    """
    Create or update a dashboard from file
    """

    # Common options
    request = {"overwrite": True, "message": f"Updated using grafana-dashboard-manager version {VERSION}"}

    # Catch the special General case where you put dashboards inside by not specifying any destination folder id or uid
    if folder_uid != "general":
        request["folderUid"] = folder_uid

    # Load the json content
    with dashboard_file.open() as file:
        request["dashboard"] = json.loads(file.read())

    # Replace any instances of folder id references which need to be 'fixed' for each Grafana target instance
    request["dashboard"] = update_dashlist_folder_ids(request)["dashboard"]

    # Dashboard ID is also specific per instance but we identify using uid instead and so this id should be null
    request["dashboard"]["id"] = None

    logger.info(f"Writing {request['dashboard']['title']} dashboard..")

    response = grafana.api.post("dashboards/db", request)
    logger.debug(f"Done: {response}")


@app.command()
def set_home_dashboard():
    """
    Attempt to set a dashboard with uid 'home' as the default Home dashboard.
    """
    logger.info("Setting home dashboard..")
    try:
        response = grafana.api.get("dashboards/uid/home")
        home_id = response["dashboard"]["id"]
    except HTTPError:
        logger.debug(f"Did not find a dashboard with uid 'home' to set as default home dashboard")
        return

    # In the UI, only starred dashboards show up as able to set as home, which isn't actually required in theory, if
    # done through the API. But since the API doesn't work, star it to make the manual step a bit easier.
    if grafana.api.isTokenAuth is False:
        if not response["meta"].get("isStarred", False):
            logger.info(grafana.api.post(f"user/stars/dashboard/{home_id}", {}))
    else:
        logger.info(grafana.api.put("org/preferences", {'homeDashboardId': home_id}))
