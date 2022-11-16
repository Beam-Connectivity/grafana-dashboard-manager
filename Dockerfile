FROM python:3.10-alpine

WORKDIR /app

RUN apk add --update --no-cache \
    	gcc \
		libressl-dev \
		musl-dev \
		libffi-dev \
		rust \
		cargo

RUN pip install --no-cache-dir poetry==1.2.0

RUN apk del \
        gcc \
        libressl-dev \
        musl-dev \
        libffi-dev \
	    rust \
	    cargo

ADD pyproject.toml            /app/pyproject.toml
ADD README.md                 /app/README.md
ADD grafana_dashboard_manager /app/grafana_dashboard_manager
ADD poetry.lock               /app/poetry.lock

RUN cd /app && poetry install

ENTRYPOINT ["poetry", "run", "grafana-dashboard-manager"]

CMD ["--help"]
