import json

from google.cloud import bigquery


def exists_table(bq_client, dataset_id, table_name):
    tables = bq_client.list_tables(dataset_id)
    for table in tables:
        if table_name == table.table_id:
            return True
    return False


def create_table(bq_client, table_id, schema):
    table = bigquery.Table(table_id, schema=schema)
    ret = bq_client.create_table(table)
    return ret


def csvloadjobjsonconfig(jsonload, skipleadingrows):
    schema = []
    for schematmp in jsonload:
        schema.append(
            bigquery.SchemaField(
                schematmp["name"],
                schematmp["type"],
                mode=schematmp.get("mode", ""),
                description=schematmp.get("description", ""),
            )
        )
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.skip_leading_rows = skipleadingrows
    job_config.schema = schema
    return job_config


def main(event, context):
    bucket_name = event["bucket"]
    file_name = event["name"]

    bq_client = bigquery.Client()

    if file_name == "data.csv":
        try:
            dataset = bigquery.Dataset(conf["project_id"] + "." + conf["dataset_name"])
            dataset.location = conf["location"]
            dataset = bq_client.create_dataset(dataset, timeout=30)
        except Exception as e:
            print(e)
            print("Dataset already exists.")

        conf = json.load(open("conf.json", "r"))

        table_id = (
            conf["project_id"] + "." + conf["dataset_name"] + "." + conf["table_name"]
        )

        schema = json.load(open("schema.json", "r"))
        job_config = csvloadjobjsonconfig(schema, conf["skip_leading_rows"])

        if not exists_table(
            bq_client,
            conf["project_id"] + "." + conf["dataset_name"],
            conf["table_name"],
        ):
            _ = create_table(bq_client, table_id, job_config.schema)

        uri = "gs://" + bucket_name + "/" + file_name
        load_job = bq_client.load_table_from_uri(uri, table_id, job_config=job_config)
        load_job.result()
