"""
Copyright (c) 2021 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.


This cli interface can be called with
(poetry install)
poetry run grafana-cli --help
"""

import logging

import typer
from rich.logging import RichHandler

import grafana_cli.dashboard
import grafana_cli.dashboard_download
import grafana_cli.dashboard_upload
import grafana_cli.folder

from .api import RestApiBasicAuth, grafana

logging.basicConfig(level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])

app = typer.Typer(add_completion=False)
app.add_typer(grafana_cli.dashboard.app, name="dashboard", help="Inspect and manage dashboards")
app.add_typer(grafana_cli.folder.app, name="folder", help="Inspect and manage folders")

app.add_typer(
    grafana_cli.dashboard_download.app,
    name="download",
    help="Retrieve current dashboards from webapp and save to json files",
)
app.add_typer(
    grafana_cli.dashboard_upload.app,
    name="upload",
    help="Inserts (and overwrites) dashboard definitions from json files to webapp",
)


@app.callback()
def main(
    host: str = typer.Option(..., help="Grafana host including 'http(s)://'"),
    username: str = typer.Option("admin", help="Grafana admin login username"),
    password: str = typer.Option(..., help="Grafana admin login password"),
    verbose: bool = typer.Option(False, help="Output debug level logging"),
):
    """
    Manage Beam deployed Grafana instances.
    """
    grafana.host = host
    grafana.username = username
    grafana.password = password
    grafana.api = RestApiBasicAuth(grafana.host, grafana.username, grafana.password)

    if verbose:
        logging.getLogger().setLevel("DEBUG")


if __name__ == "__main__":
    app()
