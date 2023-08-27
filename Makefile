.PHONY: format
format:
	poetry run pysen run format

.PHONY: lint
lint:
	poetry run pysen run lint

.PHONY: install
install:
	poetry install
	poetry run pip install google-cloud-pubsub
	poetry run pip install protobuf==3.20

.PHONY: deploy_job
deploy_job:
	cp .env job/
	gcloud run jobs deploy ${JOB_NAME} \
	--image asia-northeast1-docker.pkg.dev/${GCP_PROJECT_ID}/${AR_REPOSITORY_NAME}/job:latest \
	--region ${LOCATION}

.PHONY: exec_job
exec_job:
	gcloud run jobs execute ${JOB_NAME} --region ${LOCATION}

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
