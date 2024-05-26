"""
Copyright (c) 2024 BEAM CONNECTIVITY LIMITED

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

import argparse

from grafana_dashboard_manager.commands import download_dashboards, upload_dashboards
from grafana_dashboard_manager.global_config import GlobalConfig
from grafana_dashboard_manager.grafana import GrafanaApi
from grafana_dashboard_manager.utils import configure_logging, show_info


def app():
    """Save and update Grafana dashboards via the HTTP API"""
    parser = argparse.ArgumentParser(
        description="A cli utility that uses Grafana's HTTP API to easily save and restore dashboards."
    )

    # Parser for common options needed for all commands
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--scheme", type=str, default="https", help="http or https")
    parent_parser.add_argument("--host", type=str, required=True, help="Grafana host")
    parent_parser.add_argument("--port", type=int, default=443, help="Grafana port (default 443)")
    parent_parser.add_argument("-u", "--username", type=str, help="Grafana admin login username")
    parent_parser.add_argument("-p", "--password", type=str, help="Grafana admin login password")
    parent_parser.add_argument("-t", "--token", type=str, help="Grafana API token with admin privileges")
    parent_parser.add_argument(
        "-o",
        "--org",
        type=int,
        help="An optional property that specifies the organization to which the action is applied.",
    )
    parent_parser.add_argument("-v", "--verbose", action="count", default=0, help="Verbosity level")
    parent_parser.add_argument(
        "--non-interactive",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Auto-accept confirmation prompts",
    )
    parent_parser.add_argument(
        "--skip-home", default=False, action=argparse.BooleanOptionalAction, help="Do not set the home dashboard"
    )
    parent_parser.add_argument(
        "--skip-verify", default=False, action=argparse.BooleanOptionalAction, help="Skip HTTPS server cert validation"
    )

    # Add subcommands
    sub_parsers = parser.add_subparsers(title="Commands", required=True, help="Read/Write Dashboard JSONs:")

    # Upload
    parser_upload = sub_parsers.add_parser(
        "upload",
        help="Inserts (and overwrites) dashboard definitions from json files to webapp",
        parents=[parent_parser],
    )
    parser_upload.add_argument("-s", "--source", required=True, help="Input folder of dashboards")
    parser_upload.add_argument("--overwrite", default=False, action=argparse.BooleanOptionalAction)
    parser_upload.set_defaults(func=upload_dashboards)

    # Download
    parser_download = sub_parsers.add_parser(
        "download", help="Retrieve current dashboards from webapp and save to json files", parents=[parent_parser]
    )
    parser_download.add_argument("-d", "--destination", required=True, help="Output folder for dashboards")
    parser_download.set_defaults(func=download_dashboards)

    args = parser.parse_args()

    configure_logging(args.verbose)

    # Validate the config from the arguments into a known config object
    config = GlobalConfig.model_validate(vars(args))
    if args.verbose:
        show_info("Config", config.model_dump(exclude={"func"}))

    # API Client
    client = GrafanaApi(
        scheme=config.scheme,
        host=config.host,
        port=config.port,
        username=config.username,
        password=config.password,
        token=config.token,
        org=config.org,
        skip_verify=config.skip_verify,
        verbose=args.verbose > 0,
    )

    # Run the desired command
    config.func(config, client)


if __name__ == "__main__":
    app()
