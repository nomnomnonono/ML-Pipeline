import datetime
import os

from dotenv import load_dotenv
from google.cloud import aiplatform
from kfp import compiler, dsl

load_dotenv(".env")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
AR_REPOSITORY_NAME = os.environ.get("AR_REPOSITORY_NAME")
LOCATION = os.environ.get("LOCATION")
SOURCE_CSV_URI = os.environ.get("SOURCE_CSV_URI")
ROOT_BUCKET = os.environ.get("ROOT_BUCKET")
PIPELINE_NAME = os.environ.get("PIPELINE_NAME")

from components.preprocess.main import preprocess
from components.train.main import train


@dsl.pipeline(
    name=PIPELINE_NAME,
    description="Vertex Piplines sample",
    pipeline_root=ROOT_BUCKET,
)
def pipeline() -> None:
    preprocess_op = preprocess(src_csv_path=SOURCE_CSV_URI)

    train_op = train(dataset_uri=preprocess_op.output)

    """
    deploy_op = components.load_component_from_file("components/deploy/component.yaml")
    _ = deploy_op(
        artifact=train_task.outputs["artifact"],
        model_name="ml-pipeline-arxiv-paper-model",
        serving_container_image_uri=f"asia-northeast1-docker.pkg.dev/{PROJECT_ID}/{AR_REPOSITORY_NAME}/serving:latest",
        serving_container_environment_variables='{"APP_MODULE": "server:app"}',
        serving_container_ports=80,
        endpoint_name="ml-pipeline-arxiv-paper-endpoint",
        deploy_name="ml-pipeline-arxiv-paper-deploy",
        machine_type="n1-standard-2",
        min_replicas=1,
        project=PROJECT_ID,
        location=LOCATION,
    )
    """


compiler.Compiler().compile(
    pipeline_func=pipeline, package_path="ml-pipeline-arxiv-paper.json"
)

job = aiplatform.PipelineJob(
    display_name="ml-pipeline-arxiv-paper",
    template_path="ml-pipeline-arxiv-paper.json",
    job_id=PIPELINE_NAME
    + f"-{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-4]}",
    pipeline_root=ROOT_BUCKET,
    enable_caching=False,
    project=PROJECT_ID,
    location=LOCATION,
)

job.submit()
