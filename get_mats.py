#!/usr/bin/env python3

import datetime
import json
import re
from typing import cast

from bs4 import BeautifulSoup
import requests
import sqlite_utils


BASE_URL = "https://www.materialmaker.org"
MIN_MAT_ID = 1
MAX_MAT_ID = 763

DB_PATH = "data/material_maker.db"


def extract_data_from_json(id):
    data = {}
    json_url = f"{BASE_URL}/api/getMaterial?id={id}"
    r = requests.get(json_url)
    if r.status_code == 200 and len(r.text) > 0:
        json_data = r.json()
        for field in ["id", "name", "type", "author_id", "description", "json"]:
            if field in json_data:
                data[field] = json_data[field]
    return data


def extract_data_from_html(id):
    data = {}
    html_url = f"{BASE_URL}/material?id={id}"
    r = requests.get(html_url, allow_redirects=False)
    if r.status_code == 200:
        data["url"] = html_url
        soup = BeautifulSoup(r.text, "html.parser")

        meta_div = soup.find("meta", attrs={"property": "og:image"})
        if meta_div:
            data["thumbnail"] = meta_div["content"].strip()

        image_div = soup.find(class_="image")
        if image_div:
            img = image_div.find("img")
            if img:
                data["thumbnail_large"] = BASE_URL + img["src"].strip()

        name_div = soup.find(class_="name")
        author_link = name_div.css.select_one('a[href^="/materials?author="]')
        author_name = author_link.string
        data["author_name"] = author_name

        added_version = name_div.find("p", class_="materialOptions").find_next_sibling(
            "p"
        )
        if added_version:
            added_version_txt = added_version.string.strip()
            # Added 6/16/2023, made with Material Maker 1.3
            m = re.search(
                r"Added (.*), made with Material Maker (.*)", added_version_txt
            )
            if m:
                added_date = m.group(1)
                # convert to YYYY-MM-DD
                added_date = datetime.datetime.strptime(
                    added_date, "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
                data["added_at"] = added_date
                mm_version = m.group(2)
                data["mm_version"] = mm_version

        tags_div = name_div.find("div", class_="tags")
        if tags_div:
            license = tags_div.css.select_one('a[href^="materials?license_mask="]')
            if license:
                data["license"] = license.string.strip()
            tags = tags_div.css.select('a[href^="materials?tag="]')
            if tags:
                data["tags"] = json.dumps([tag.string.strip() for tag in tags])
    return data


def generate_filename(name):
    filename = re.sub(r"[^\w]+", "_", name)
    filename = filename.lower()
    filename += ".ptex"
    return filename


def get_material(id):
    data = {}
    data.update(extract_data_from_json(id))
    data.update(extract_data_from_html(id))

    if "name" in data:
        data["filename"] = generate_filename(data["name"])
    return data


def main():
    db = sqlite_utils.Database(DB_PATH)
    ensure_tables(db)

    for id in range(MIN_MAT_ID, MAX_MAT_ID + 1):
        data = get_material(id)
        if len(data) > 0:
            # pp(data)
            db["materials"].insert(data, replace=True)
            print(f"saved {id}")
        else:
            print(f"skipped {id}")

    # XXX fix tags
    # for row in db.query("select id, tags from materials"):
    #     if row['tags']:
    #         print(row['id'], row['tags'])
    #         tags = row['tags'].split(',')
    #         db['materials'].update(row['id'], {'tags': json.dumps(tags)})


def _ensure_table(db: sqlite_utils.Database, table_name: str, *args, **kwargs):
    if table_name not in db.table_names():
        table = cast(sqlite_utils.db.Table, db.table(table_name))
        table.create(*args, **kwargs)


def ensure_tables(db: sqlite_utils.Database):
    _ensure_table(
        db,
        "materials",
        {
            "id": int,
            "name": str,
            "type": int,
            "url": str,
            "author_id": int,
            "author_name": str,
            "description": str,
            "thumbnail": str,
            "thumbnail_large": str,
            "filename": str,
            "license": str,
            "tags": str,
            "added_at": str,
            "mm_version": str,
            "json": str,
        },
        pk="id",
    )


if __name__ == "__main__":
    main()
