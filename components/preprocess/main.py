import os

from dotenv import load_dotenv
from kfp.v2.dsl import OutputPath, component

load_dotenv(".env")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
AR_REPOSITORY_NAME = os.environ.get("AR_REPOSITORY_NAME")


@component(
    base_image=f"asia-northeast1-docker.pkg.dev/{PROJECT_ID}/{AR_REPOSITORY_NAME}/preprocess:latest"
)
def preprocess(src_csv_path: str, dataset_uri: OutputPath("Dataset")) -> None:
    from pathlib import Path

    import pandas as pd
    from sklearn.model_selection import train_test_split

    df = pd.read_csv(src_csv_path)
    print(f"Load CSV from: {src_csv_path}")

    df["target"] = df["category"].map({"cs.CV": 0, "cs.CL": 1, "cs.RO": 2})
    df_train, df_val = train_test_split(df, test_size=0.2, random_state=42)

    dataset_dir = Path(dataset_uri)
    dataset_dir.mkdir(parents=True, exist_ok=True)
    df_train.to_csv(dataset_dir / "train.csv", index=False)
    df_val.to_csv(dataset_dir / "val.csv", index=False)
    print(f"Save train/val data in: {dataset_dir}")
