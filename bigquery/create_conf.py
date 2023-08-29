import json
import os

from dotenv import load_dotenv

load_dotenv(".env")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
DATASET_NAME = os.environ.get("DATASET_NAME")
TABLE_NAME = os.environ.get("TABLE_NAME")
LOCATION = os.environ.get("LOCATION")

conf = {}
conf["skip_leading_rows"] = 1
conf["project_id"] = PROJECT_ID
conf["dataset_name"] = DATASET_NAME
conf["table_name"] = TABLE_NAME
conf["location"] = LOCATION

with open("bigquery/conf.json", "w") as f:
    json.dump(conf, f, indent=4)
