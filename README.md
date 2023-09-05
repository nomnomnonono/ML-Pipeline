# ML-Pipeline-of-Paper-Category-Classification
Arxiv APIで取得した論文データについて、タイトルから主カテゴリを予測する分類器を学習、デプロイする

## Requirements
- Poetry
- gcloud CLI
- docker compose

## Setup
### GCP Authentification
```bash
$ gcloud auth login
$ gcloud components install pubsub-emulator
```

### Install Dependencies
```bash
$ make install
```

### Environmental Variables
```bash
$ vi .env
```

- 以下の情報を記入＋環境変数としてexportしておく
```bash
GCP_PROJECT_ID=your project id
TOPIC_ID=your topic id
AR_REPOSITORY_NAME=artifact registory repository name
LOCATION=asia-northeast1
DATA_BUCKET=gs://xxx
SOURCE_CSV_URI=gs://xxx/data.csv
CONFIG_FILE_URI=gs:/xxx/config.json
ROOT_BUCKET=gs://yyy
JOB_NAME=cloud run job name
SCHEDULER_NAME=cloud scheduler name
DATASET_NAME=dataset name
TABLE_NAME=table name
BQ_FUNC_NAME=cloud functions name to use bigquery
```

## Boot MLflow Server
```bash
$ make mlflow
```

## Build & Push Docker Image
```bash
$ gcloud auth configure-docker asia-northeast1-docker.pkg.dev
$ gcloud artifacts repositories create $AR_REPOSITORY_NAME --location=$LOCATION --repository-format=docker
$ docker compose build
$ docker compose push
```

## Deploy Cloud Functions to Use BiqQuery
データセットが更新されたらBigQueryも自動更新する関数をデプロイする
```bash
$ make deploy_bq_func
```

## Cloud Run Job to Scrape Paper Data
### Deploy
```bash
$ make deploy_job
```

### Exec
下記コマンドを実行すると前回実行時点からの差分となる論文情報が取得される
```bash
$ make exec_job
```

### Create Scheduler
Cloud Run Jobの定期実行をしたい場合は下記コマンドを実行してください（デフォルトは月1回）
```bash
$ make create_scheduler
```

## Exec Pipeline
```bash
$ make pipeline
```
