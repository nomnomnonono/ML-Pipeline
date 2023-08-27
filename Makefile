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

.PHONY: pipeline
pipeline:
	poetry run python pipeline.py
