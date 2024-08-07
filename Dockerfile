FROM python:3.11-slim as python-build

ENV POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry self add poetry-plugin-export
RUN poetry config warnings.export false

# copy project requirement files here to ensure they will be cached.
WORKDIR /build
COPY poetry.lock pyproject.toml ./
RUN poetry export -f requirements.txt \
    --without-hashes \
    --without dev \
    > requirements.txt


######################################################

FROM python:3.11-slim as app
ENV APP_PATH="/app/grafana-dashboard-manager/"
WORKDIR $APP_PATH

COPY --from=python-build /build/requirements.txt $APP_PATH
COPY --from=python-build /build/pyproject.toml $APP_PATH
COPY README.md $APP_PATH
COPY grafana_dashboard_manager "$APP_PATH/grafana_dashboard_manager"

RUN pip install -r requirements.txt
RUN pip install $APP_PATH

ENTRYPOINT ["python", "grafana_dashboard_manager"]
