FROM python:3.11-bullseye AS python-build

ENV POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry self add poetry-plugin-export@1.6.0
RUN poetry config warnings.export false

# copy project requirement files here to ensure they will be cached.
WORKDIR /build
COPY poetry.lock pyproject.toml ./
RUN poetry export -f requirements.txt \
    --without-hashes \
    --without dev \
    > requirements.txt


######################################################

FROM python:3.11-bullseye AS app
ENV APP_PATH="/app/grafana-dashboard-manager/"
WORKDIR $APP_PATH

COPY --from=python-build /build/requirements.txt $APP_PATH
COPY --from=python-build /build/pyproject.toml $APP_PATH
COPY README.md $APP_PATH
COPY grafana_dashboard_manager "$APP_PATH/grafana_dashboard_manager"

RUN pip install -r requirements.txt
RUN pip install $APP_PATH

RUN apt-get update && apt-get install -y \
        vim-tiny \
        nano \
        netcat-openbsd \
        jq \
        bash \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl v1.33.2
RUN curl -LO "https://dl.k8s.io/release/v1.33.2/bin/linux/amd64/kubectl" \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
    && rm kubectl

# Install kustomize v5.4.1
RUN curl -L https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv5.4.1/kustomize_v5.4.1_linux_amd64.tar.gz \
    | tar -xz && mv kustomize /usr/local/bin/

#ENTRYPOINT ["python", "grafana_dashboard_manager"]
ENTRYPOINT ["/bin/bash"]
