# grafana-dashboard-manager

![CodeQL](https://github.com/Beam-Connectivity/grafana-dashboard-manager/actions/workflows/codeql-analysis.yml/badge.svg)

## Introduction

A simple CLI utility for importing or exporting dashboard JSON definitions using the Grafana HTTP API.

This can be used for:

- Backing up your dashboards that already exist within your Grafana instance, e.g. if you are migrating from the internal SQLite database to MySQL.
- Updating dashboard files for your Infrastructure-as-Code for use with [Grafana dashboard provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/#dashboards).
- Making tweaks to dashboard JSON files directly and updating Grafana with one command.

### Features

- Mirrors the folder structure between a local set of dashboards and Grafana, creating folders where necessary.
- Ensures links to dashboards folders in a `dashlist` Panel are consistent with the Folder IDs - useful for deploying one set of dashboards across multiple Grafana instances, for instance across environments.

### Workflow

The intended workflow is:

1. Create a dashboard and save it in the desired folder from within the Grafana web GUI
2. Use `grafana-dashboard-manager` to extract the new dashboards and save them to a local directory or version control system.
3. Dashboards can be created or updated from the local store and uploaded back into Grafana.

## Installation

### Install via _[pip](https://pypi.org/project/pip/)_:

```shell
pip install grafana-dashboard-manager
```

### Install from source - requires _[Poetry](https://python-poetry.org/)_ on your system:

```shell
cd /path/to/grafana-dashboard-manager
poetry install
```

## Usage

### Credentials

It is important to note that the **admin** login username and password are required, and its selected organization must be correct, if you are accessing the API using `--username` and `--password`. Alternatively, the API Key must have **admin** permissions if you are accessing the API using `--token`.

For more help, see the full help text with `poetry run grafana-dashboard-manager --help`.

### Download dashboards from web to solution-data using the Grafana admin user

```shell
poetry run grafana-dashboard-manager \
    --host https://my.grafana.com \
    --username admin_username --password admin_password \
    download all \
    --destination-dir /path/to/dashboards/
```

### Download dashboards from web to solution-data using a Grafana admin API Key

```shell
poetry run grafana-dashboard-manager \
    --host https://my.grafana.com \
    --token admin_api_key \
    download all \
    --destination-dir /path/to/dashboards/
```

### Upload dashboards from solution-data to web using the Grafana admin user

```shell
poetry run grafana-dashboard-manager \
    --host https://my.grafana.com \
    --username admin_username --password admin_password \
    upload all \
    --source-dir /path/to/dashboards/
```

### Upload dashboards from solution-data to web using a Grafana admin API Key

```shell
poetry run grafana-dashboard-manager \
    --host https://my.grafana.com \
    --token admin_api_key \
    upload all \
    --source-dir /path/to/dashboards/
```

**Please note:** if your Grafana is not hosted on port 80/443 as indicated by the protocol prefix, the port needs to be specified as part of the `--host` argument. For example, a locally hosted instance on port 3000: `--host http://localhost:3000`.

## Limitations

- The home dashboard new deployment needs the default home dashboard to be manually set in the web UI, as the API to set the organisation default dashboard seems to be broken, at least on v8.2.3.
- Currently expects a hardcoded `home.json` dashboard to set as the home.
- Does not handle upload of dashboards more deeply nested than Grafana supports.
- Does not support multi-organization deployments.
