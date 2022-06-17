"""
Copyright (c) 2021 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.


This cli interface can be called with
(poetry install)
poetry run grafana-dashboard-manager --help
"""

import logging

import typer
from rich.logging import RichHandler

import grafana_dashboard_manager.dashboard
import grafana_dashboard_manager.dashboard_download
import grafana_dashboard_manager.dashboard_upload
import grafana_dashboard_manager.folder

from .api import RestApiBasicAuth, grafana

logging.basicConfig(level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])

app = typer.Typer(add_completion=False)
app.add_typer(grafana_dashboard_manager.dashboard.app, name="dashboard", help="Inspect and manage dashboards")
app.add_typer(grafana_dashboard_manager.folder.app, name="folder", help="Inspect and manage folders")

app.add_typer(
    grafana_dashboard_manager.dashboard_download.app,
    name="download",
    help="Retrieve current dashboards from webapp and save to json files",
)
app.add_typer(
    grafana_dashboard_manager.dashboard_upload.app,
    name="upload",
    help="Inserts (and overwrites) dashboard definitions from json files to webapp",
)


@app.callback()
def main(
    host: str = typer.Option(..., help="Grafana host including 'http(s)://'"),
    username: str = typer.Option("admin", help="Grafana admin login username"),
    password: str = typer.Option(None, help="Grafana admin login password"),
    token: str = typer.Option(None, help="Grafana API token with admin privileges"),
    verbose: bool = typer.Option(False, help="Output debug level logging"),
):
    """
    Manage Beam deployed Grafana instances.
    """
    grafana.host = host
    grafana.credentials = token if token else (username, password)
    grafana.api = RestApiBasicAuth(grafana.host, grafana.credentials)

    if verbose:
        logging.getLogger().setLevel("DEBUG")


if __name__ == "__main__":
    app()
