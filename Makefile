include .env
export $(shell sed 's/=.*//' .env)

DOCKER_RUN=docker run --rm -it -w /app -u $(UID):$(GID) -v $(PWD)/data:/app/data grafana-dashboard-manager:latest --host $(HOST) --token $(TOKEN) --verbose

.PHONY: build
build:
	docker build -t grafana-dashboard-manager:latest -f Dockerfile .

.PHONY: download
download: build
	$(DOCKER_RUN) download all --destination-dir /app/data

.PHONY: upload
upload: build
	$(DOCKER_RUN) upload all --source-dir /app/data

.PHONY: home
home: build
	$(DOCKER_RUN) upload set-home-dashboard

