import os

from dotenv import load_dotenv
from kfp import compiler, components, dsl

load_dotenv(".env")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
AR_REPOSITORY_NAME = os.environ.get("AR_REPOSITORY_NAME")
LOCATION = os.environ.get("LOCATION")
SOURCE_CSV_URI = os.environ.get("SOURCE_CSV_URI")
ROOT_BUCKET = os.environ.get("ROOT_BUCKET")


@dsl.pipeline(
    name="vertex-pipelines-sample",
    description="Vertex Piplines sample",
    pipeline_root=ROOT_BUCKET,
)
def pipeline() -> None:
    preprocess_op = components.load_component_from_file(
        "components/preprocess/component.yaml"
    )
    preprocess_task = preprocess_op(src_csv=SOURCE_CSV_URI)

    train_op = components.load_component_from_file("components/train/component.yaml")
    train_task = train_op(dataset=preprocess_task.outputs["dataset"])
    train_task.custom_job_spec = {
        "displayName": train_task.name,
        "jobSpec": {
            "workerPoolSpecs": [
                {
                    # "containerSpec": {
                    #    "imageUri": f"asia-northeast1-docker.pkg.dev/{PROJECT_ID}/{AR_REPOSITORY_NAME}/train:latest", # train_task.container.image
                    #    "args": {"dataset": preprocess_task.outputs["dataset"]}, # train_task.arguments,
                    # },
                    "machineSpec": {"machineType": "n1-standard-2"},
                    "replicaCount": 1,
                }
            ],
        },
    }

    evaluate_op = components.load_component_from_file(
        "components/evaluate/component.yaml"
    )
    _ = evaluate_op(
        dataset=preprocess_task.outputs["dataset"],
        artifact=train_task.outputs["artifact"],
    )

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


compiler.Compiler().compile(
    pipeline_func=pipeline, package_path="ml-pipeline-arxiv-paper.json"
)
