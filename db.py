#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue April 20 2021

@author: Xiaoyu
"""
from pathlib import Path
from typing import Any
from playhouse.shortcuts import model_to_dict
from peewee import SqliteDatabase, Model  # type: ignore
from peewee import IntegerField, CharField, DateTimeField, TextField  # type: ignore
from typing import Dict, Union, Iterator, List
import os
import json
from peewee import chunked

data_dir = Path("data")
db_name = "wapo_docs_50k.db"
db_path = data_dir.joinpath(db_name)
wapo_jl_path = "data/subset_wapo_50k_sbert_ft_filtered.jl"

# create a sqlite database stored in pa4_data/wapo_docs.db
# http://docs.peewee-orm.com/en/latest/peewee/database.html
db = SqliteDatabase(
    Path(__file__).parent.joinpath(db_path),
    pragmas={
        "journal_mode": "wal",  # allow readers and writers to co-exist
        "cache_size": -1 * 64000,  # 64 Mb
        "foreign_keys": 1,  # enforce foreign-key constraints
        "ignore_check_constraints": 0,  # enforce CHECK constraints
        "synchronous": 0,  # let OS handle fsync (use with caution)
    },
)


class BaseModel(Model):
    class Meta:
        database = db


class Doc(BaseModel):
    """
    define your WAPO doc data model (table schema)
    reference: http://docs.peewee-orm.com/en/latest/peewee/models.html#
    # Model class: Database table
    # Field instance: Column on a table
    # Model instance: Row in a database table
    """
    doc_id = IntegerField(primary_key=True)
    title = CharField()
    author = CharField()
    annotation = CharField()
    published_date = DateTimeField(formats='%Y/%m/%d')
    content_str = TextField()


@db.connection_context()
def create_tables():
    """
    create and populate the wapo doc table. Consider using bulk insert to load data faster
    reference:
    http://docs.peewee-orm.com/en/latest/peewee/querying.html#bulk-inserts
    :return:
    """
    db.create_tables([Doc], safe=True)  # Create schema
    wapo_docs = list(load_wapo(wapo_jl_path))
    print("populating the table")
    for batch in chunked(wapo_docs, 100):
        Doc.insert_many(batch).execute()  # populate the table


@db.connection_context()
def query_doc(doc_id: int) -> Dict[str, Any]:
    """
     given the doc_id, get the document dict
     reference:
     http://docs.peewee-orm.com/en/latest/peewee/querying.html#selecting-a-single-record
     http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#model_to_dict
    :param doc_id:
    :return:
    """
    return model_to_dict(Doc.get_by_id(doc_id))


def load_wapo(wapo_jl_path: Union[str, os.PathLike]) -> Iterator[Dict]:
    """
    load_wapo in HW3:
        {
        "id": 1,
        "title": "Many Iowans still don't know who they will caucus for",
        "author": "Jason Horowitz",
        "published_date": 1325380672000,
        "content_str": "Iran announced a nuclear fuel breakthrough and test-fired ..."
        }
    It should be similar to the load_wapo in HW3 with two changes:
    - for each yielded document dict, use "doc_id" instead of "id" as the key to store the document id.
    - convert the value of "published_date" to a readable format e.g. 2021/3/15. You may consider using python datatime package to do this.
    """

    with open(wapo_jl_path, "r") as f:
        idx = 0
        for line in f:
            data = json.loads(line)
            val = {"doc_id": idx,
                   "title": (data["title"] if data["title"] else "Untitled"),
                   "author": data["author"],
                   "annotation": data["annotation"],  # could be empty string
                   "published_date": data["published_date"],
                   "content_str": data['content_str']
                   }
            yield val
            idx += 1


if __name__ == "__main__":
    # delete the existed ones before rebuild
    if db_path.exists():
        print("deleting...")
        Path(__file__).parent.joinpath(db_path).unlink()
    df_path_shm = data_dir.joinpath(f"{db_name}-shm")
    if df_path_shm.exists():
        Path(__file__).parent.joinpath().unlink(df_path_shm)
        Path(__file__).parent.joinpath(data_dir.joinpath(f"{db_name}-wal")).unlink()
    print("creating...")
    create_tables()
    print("Done...")
    for i in range(10):
        print(query_doc(i))
