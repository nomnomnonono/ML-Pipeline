# ML-Pipeline
Arxiv APIで取得した論文データについて、タイトルから主カテゴリを予測する分類器を学習、デプロイする

## Requirements
- Poetry
- gcloud CLI
- docker compose

## Setup
### GCP Authentification
```bash
$ gcloud auth login
```

### Install Dependencies
```bash
$ poetry install
```

### Environmental Variables
```bash
GCP_PROJECT_ID=your project id
AR_REPOSITORY_NAME=artifact registory repository name
LOCATION=asia-northeast1
SOURCE_CSV_URI=gs://xxx/data.csv
ROOT_BUCKET=gs://yyy
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
$ gcloud artifacts repositories create $AR_REPOSITORY_NAME --location=$LOCATION --repository-format=docker
$ docker compose build
$ docker compose push
```

## Exec Pipeline
```bash
$ make pipeline
```
