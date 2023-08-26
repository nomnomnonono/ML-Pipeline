# ML-Pipeline

## Requirements
- Poetry
- gcloud CLI
- docker compose

## Setup
```bash
$ gcloud auth login
$ poetry install
```

## Create Dataset
```bash
$ gsutil mb -l asia-northeast gs://ml-pipeline-arxiv-paper-data
$ gsutil mb -l asia-northeast gs://ml-pipeline-arxiv-paper-artifact
$ make data
```

## Build & Push Docker Image
```bash
$ gcloud auth configure-docker asia-northeast1-docker.pkg.dev
$ gcloud artifacts repositories create ml-pipeline-arxiv-paper --location=asia-northeast1 --repository-format=docker
$ docker compose build
$ docker compose push
```
