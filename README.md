# grafana-dashboard-manager

![CodeQL](https://github.com/Beam-Connectivity/grafana-dashboard-manager/actions/workflows/codeql-analysis.yml/badge.svg)

A simple CLI utility for importing and exporting dashboards as JSON using the Grafana HTTP API.

This can be used for:

- Backing up your dashboards that already exist within your Grafana instance, e.g. if you are migrating from the internal SQLite database to MySQL.
- Updating dashboard files for your Infrastructure-as-Code for use with [Grafana dashboard provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/#dashboards).
- Making tweaks to dashboard JSON files directly and updating Grafana with one command.

## Features

- Mirrors the folder structure between a local set of dashboards and Grafana, creating folders where necessary.
- Ensures links to dashboards folders in a `dashlist` Panel are consistent with the Folder UIDs - useful for deploying one set of dashboards across multiple Grafana instances, for instance across environments.

## Usage

> For detailed command help, see the full help text with the `--help` option.

### Credentials

It is important to note that the **admin** login username and password are required, and its selected organization must be correct, if you are accessing the API using `--username` and `--password`. Alternatively, a provided API Key must have **admin** permissions if you are accessing the API using `--token`.

### Docker

A Dockerfile is provided. To build and run:

```sh
docker build -t grafana-dashboard-manager:latest .
docker run grafana-dashboard-manager --help
```

### From PyPI

Install via _[pip](https://pypi.org/project/pip/)_:

```sh
pip install grafana-dashboard-manager
```

### From source

Install dependencies and run with _[Poetry](https://python-poetry.org/)_

```sh
cd /path/to/grafana-dashboard-manager
poetry install
poetry run python ./grafana_dashboard_manager --help
```

## Workflow

The intended workflow is:

1. Download dashboards and to a local directory or version control system for backup and change control.
1. Replicate across multiple Grafana installs or restore a previous install by uploading the saved dashboards.

## Usage Examples

These examples use `docker run` commands, but the commands are the same regardless of run method.

Download dashboards using the Grafana admin user:

```sh
docker run grafana-dashboard-manager \
    download \
    --scheme https \
    --host my.grafana.example.com \
    --username $USERNAME --password $PASSWORD \
    --destination /path/to/dashboards/
```

Download dashboards using a Grafana admin API Key:

```sh
docker run grafana-dashboard-manager \
    download \
    --scheme https \
    --host my.grafana.example.com \
    --token $API_KEY \
    --destination /path/to/dashboards/
```

Upload dashboards using the Grafana admin user, to a local instance for testing

```sh
docker run grafana-dashboard-manager \
    upload \
    --scheme http \
    --port 3000 \
    --host localhost \
    --username $USERNAME --password $PASSWORD \
    --source /path/to/dashboards/
```

Upload dashboards using a Grafana admin key without any user prompts:

```sh
docker run grafana-dashboard-manager \
    upload \
    --scheme http \
    --port 3000 \
    --host localhost \
    --token $API_KEY \
    --source /path/to/dashboards/
```

##  Notes

- The scheme is `https` and port is 443 by default. If your Grafana is not hosted with https on 443, the scheme and port needs to be specified using the `--scheme` and `--port` options respectively.
- The `version` of the dashboard is removed of the json files in order to allow overwriting and creation of dashboards as new.
- URL encoding of strings is handled by httpx and so characters such as `/` in folder names is supported.
- When uploading, setting the home dashboard from the `home.json` file can be disabled with the option `--skip-home`.

## Limitations

- Does not support the experimental nested folders in Grafana. Only one level of folders is supported.
- Does not support multi-organization deployments.
