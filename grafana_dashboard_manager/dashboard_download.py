"""
Copyright (c) 2021 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.


Download dashboards from a Grafana web instance.
"""
import json
import logging
from pathlib import Path
from typing import Dict

import rich
import typer
from rich.tree import Tree

from .api import grafana
from .dashboard import update_dashlist_folder_ids
from .tree import walk_directory

app = typer.Typer()
logger = logging.getLogger()


@app.command()
def all(
    destination_dir: Path = typer.Option(
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
    logger.info(f"Pulling all dashboards into {destination_dir}...")

    # Get all dashboards within each folder and write to files
    folders = grafana.api.get("folders")
    logger.info(f"Folders found: {[x['title'] for x in folders]}")

    for folder in folders:
        logger.info(f"Getting dashboards from the {folder['title']} folder..")
        # Find all dashboards in the folder
        _write_dashboards_to_local_folder_from_grafana_folder(folder, destination_dir)

    # Special case for the General folder
    _write_dashboards_to_local_folder_from_grafana_folder({"title": "General"}, destination_dir)

    tree = Tree(
        f":open_file_folder: [link file://{destination_dir}]{destination_dir}",
        guide_style="bold bright_blue",
    )
    rich.print(walk_directory(destination_dir, tree))

    logger.info("✅")

# =============


def _write_dashboards_to_local_folder_from_grafana_folder(folder: Dict, destination_dir: Path) -> None:
    """
    Finds dashboards within a given folder and writes them to the destination_dir/folder name
    """
    # The General folder (id=0) is special and is not part of the Folder API so query for it separately
    if folder["title"] == "General":
        folder_id = 0
    else:
        folder_id = folder["id"]

    for dashboard in grafana.api.get(f"search?folderIds={folder_id}&type=dash-db"):
        logger.info(f"Found {dashboard['title']} dashboard in folder {folder['title']}")

        try:
            dashboard_definition = grafana.api.get(f"dashboards/uid/{dashboard['uid']}")

            # Update references in dashboard pickers to folder ids, as they are auto generated
            dashboard_definition = update_dashlist_folder_ids(dashboard_definition)

            # Write it to file
            dashboard_file: Path = (
                    destination_dir / folder["title"] / f"{dashboard['title'].lower().replace(' ', '_')}.json"
                    )
            dashboard_file.parent.mkdir(parents=True, exist_ok=True)
            dashboard_file.write_text(json.dumps(dashboard_definition["dashboard"], indent=2))
            logger.info(f"Successfully saved {dashboard['title']} dashboard to {dashboard_file}")
        except Exception:
            logger.exception(f"❌ An exception occurred with {dashboard['title']}")
