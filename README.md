# grafana-dashboard-manager

![CodeQL](https://github.com/Beam-Connectivity/grafana-dashboard-manager/actions/workflows/codeql-analysis.yml/badge.svg)


A simple cli utility for importing or exporting dashboard json definitions using the Grafana HTTP API.

This may be useful for:

- Backing up your dashboards that already exist within your Grafana instance, e.g. if you are migrating from the internal sqlite database to MySQL.
- Updating dashboard files for your Infrastructure-as-Code, for use with Grafana dashboard provisioning.
- Making tweaks to dashboard JSON files directly and updating Grafana with one command.

Notable features:

- Mirrors the folder structure between a local set of dashboards and Grafana, creating folders where necessary.
- Ensures links to dashboards folders in a `dashlist` Panel are consistent with the Folder IDs - useful for deploying one set of dashboards across mulitple Grafana instances, e.g. for dev, test, prod environments.

### Workflow

The intended development process is:

1. Develop existing dashboard, or create a new one and save it in the web UI.
2. Ensure the dashboard is in the desired folder.
3. Use `grafana-dashboard-manager` to extract the new dashboards and save them to a local directory.
4. Dashboards can be created/updated from the local directory back into Grafana.

# Usage

#### Installation

Dependencies are managed with poetry.

Install from pypi:

```bash
$ pip install grafana-dashboard-manager
```

Install from source (requires [poetry](https://python-poetry.org/) on your system)

```bash
$ cd /path/to/grafana-dashboard-manager
$ poetry install
```

Note that the admin login user and password are required, and its selected organization is correct.

See the full help text with `poetry run grafana-dashboard-manager --help`

### Download dashboards from web to solution-data

```bash
poetry run grafana-dashboard-manager \
    --host https://my.grafana.com \
    --username admin --password mypassword \
    download all \
    --destination-dir /path/to/dashboards/
```

### Upload dashboards from solution-data to web

```bash
poetry run grafana-dashboard-manager \
    --host https://my.grafana.com \
    --username admin --password mypassword \
    upload all \
    --source-dir /path/to/dashboards/
```

N.B. if your Grafana is not at port 80/443 as indicated by the protocol prefix, the port needs to be specified as part of the `--host` argument, e.g. for a locally hosted instance on port 3000: `--host http://localhost:3000`

## Limitations

- The home dashboard new deployment needs the default home dashboard to be manually set in the web UI, as the API to set the organisation default dashboard seems to be broken, at least on v8.2.3.

- Currently expects a hardcoded 'home.json' dashboard to set as the home.

- Does not handle upload of dashboards more deeply nested than Grafana supports.

- Does not support multi-organization deployments
