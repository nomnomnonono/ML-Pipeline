import json
import os
from datetime import datetime, timedelta
from io import BytesIO

import arxiv
import pandas as pd
from dotenv import load_dotenv
from google.cloud import storage

CATEGORIES = ["cs.CV", "cs.CL", "cs.RO"]


class Scraper:
    def __init__(self):
        load_dotenv(".env")
        self.client = storage.Client()
        self.source_csv_uri = (
            os.environ.get("SOURCE_CSV_URI").lstrip("gs://").split("/", maxsplit=1)
        )
        self.config_file_uri = (
            os.environ.get("CONFIG_FILE_URI").lstrip("gs://").split("/", maxsplit=1)
        )

    def run(self):
        try:
            bucket = self.client.bucket(self.config_file_uri[0])
            blob = bucket.blob(self.config_file_uri[1])
            content = blob.download_as_bytes()
            config = json.load(BytesIO(content))
        except:
            print("config file not found")
            config = {
                "before": "{:%Y%m%d%H%M%S}".format(datetime.now() - timedelta(weeks=4))
            }

        config = self.scrape_paper(config)
        self.save_config(config, self.config_file_uri[0], self.config_file_uri[1])

    def scrape_paper(self, config: dict) -> dict:
        try:
            bucket = self.client.bucket(self.source_csv_uri[0])
            blob = bucket.blob(self.source_csv_uri[1])
            content = blob.download_as_bytes()
            df = pd.read_csv(BytesIO(content))
        except:
            print("csv file not found")
            df = pd.DataFrame(
                [],
                columns=[
                    "title",
                    "category",
                    "author",
                    "year",
                    "month",
                    "date",
                    "link",
                ],
            )

        idx = max(df.index) if len(df) > 0 else 0

        time_query, config = self.define_time_range(config)

        for category in CATEGORIES:
            print(f"scrapping {category}")
            query = f"cat:{category} AND " + time_query
            search = arxiv.Search(
                query=query,
                sort_by=arxiv.SortCriterion.SubmittedDate,
            )

            for result in search.results():
                if result.primary_category != category:
                    continue

                year, month, date = str(result.published).split(" ")[0].split("-")
                df.loc[idx] = [
                    result.title.replace("'", "").replace('"', ""),
                    category,
                    str(result.authors[0]),
                    int(year),
                    int(month),
                    int(date),
                    str(result.links[0]),
                ]

                idx += 1

        df.drop_duplicates(inplace=True)
        bucket = self.client.bucket(self.source_csv_uri[0])
        blob = bucket.blob(self.source_csv_uri[1])
        blob.upload_from_string(df.to_csv(index=False), "text/csv")
        return config

    def define_time_range(self, config: dict) -> tuple[str, dict]:
        now = "{:%Y%m%d%H%M%S}".format(datetime.now())
        time_query = f"submittedDate:[{config['before']} TO {now}]"
        config["before"] = now
        return time_query, config

    def save_config(self, config: dict, bucket_name: str, blob_name: str) -> None:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(json.dumps(config), "application/json")


if __name__ == "__main__":
    scraper = Scraper()
    scraper.run()
