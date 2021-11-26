"""
Copyright (c) 2021 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.


CLI commands to interact with Dashboard Folders in Grafana
"""

import json
import logging

import rich
import typer

from .api import grafana

app = typer.Typer()
logger = logging.getLogger()

ARG_UID = typer.Argument(..., help="The unique identifier for the dashboard")
ARG_TITLE = typer.Argument(..., help="The display title for the dashboard")
BASE_RESOURCE = "folders"


@app.command()
def create(title: str = ARG_UID):
    """
    Create a new dashboard folder.
    """
    # The dashboard uid is a lower snakecased title
    request = {"uid": title.lower().replace(" ", ""), "title": title}
    response = grafana.api.post(BASE_RESOURCE, request)
    rich.print_json(json.dumps(response))


@app.command()
def show():
    """
    Show the names and details of existing dashboard folders.
    """
    response = grafana.api.get(BASE_RESOURCE)
    rich.print_json(json.dumps(response))


@app.command()
def update(uid: str = ARG_UID, title: str = ARG_TITLE):
    """
    Update the title for an existing dashboard folder
    """
    request = {"title": title, "overwrite": True}
    response = grafana.api.put(f"{BASE_RESOURCE}/{uid}", request)
    rich.print_json(json.dumps(response))


@app.command()
def delete(uid: str = ARG_UID):
    """
    Delete an existing folder identified by UID along with all dashboards (and their alerts) stored in the folder.
    """
    response = grafana.api.delete(f"{BASE_RESOURCE}/{uid}")
    rich.print_json(json.dumps(response))
