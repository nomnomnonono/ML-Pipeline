import datetime
import json
import os

import arxiv
import pandas as pd

CATEGORIES = ["cs.CV", "cs.CL", "cs.RO"]


def scrape_paper(config: dict) -> dict:
    if os.path.exists("data.csv"):
        df = pd.read_csv("data.csv")
    else:
        df = pd.DataFrame(
            [], columns=["title", "category", "author", "year", "month", "date", "link"]
        )

    idx = max(df.index) if len(df) > 0 else 0

    time_query, config = define_time_range(config)

    for category in CATEGORIES:
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

    df.to_csv("data.csv", index=False)

    return config


def define_time_range(config: dict) -> tuple[str, dict]:
    now = "{:%Y%m%d%H%M%S}".format(datetime.datetime.now())
    time_query = f"submittedDate:[{config['before']} TO {now}]"
    config["before"] = now
    return time_query, config


def save_config(config: dict, file_path: str) -> None:
    with open(file_path, "w") as f:
        json.dump(config, f, indent=4)


if __name__ == "__main__":
    config = json.load(open("config.json"))
    config = scrape_paper(config)
    save_config(config, "config.json")
