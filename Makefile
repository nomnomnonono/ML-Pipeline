.PHONY: format
format:
	poetry run pysen run format

.PHONY: lint
lint:
	poetry run pysen run lint

.PHONY: install
install:
	poetry install
	poetry run pip install --upgrade pip
	poetry run pip install google-cloud-pubsub
	poetry run pip install google-cloud-aiplatform
	poetry run pip install google-cloud-bigquery
	poetry run pip install protobuf==3.20

.PHONY: docker
docker:
	cp .env components/preprocess/
	cp .env components/train/
	cp .env components/deploy/
	docker compose build
	docker compose push

.PHONY: deploy_job
deploy_job:
	gsutil mb ${DATA_BUCKET}
	gsutil mb ${ROOT_BUCKET}
	cp .env job/
	gcloud run jobs deploy ${JOB_NAME} \
	--image asia-northeast1-docker.pkg.dev/${GCP_PROJECT_ID}/${AR_REPOSITORY_NAME}/job:latest \
	--region ${LOCATION}

.PHONY: exec_job
exec_job:
	gcloud run jobs execute ${JOB_NAME} --region ${LOCATION}

.PHONY: deploy_bq_func
deploy_bq_func:
	poetry run python bigquery/create_conf.py
	gcloud functions deploy ${BQ_FUNC_NAME} \
	--gen2 \
	--trigger-event=google.storage.object.finalize \
	--trigger-resource=${DATA_BUCKET} \
	--region=${LOCATION} \
	--runtime=python310 \
	--source=bigquery/ \
	--entry-point=main

.PHONY: create_scheduler
create_scheduler:
	gcloud scheduler jobs create http ${SCHEDULER_NAME} \
	--location asia-northeast1 \
	--schedule="0 0 1 * *" \
	--uri="https://asia-northeast1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${GCP_PROJECT_ID}/jobs/${JOB_NAME}:run" \
	--http-method POST \

.PHONY: pipeline
pipeline:
	poetry run python pipeline.py

.PHONY: mlflow
mlflow:
	poetry run mlflow ui
