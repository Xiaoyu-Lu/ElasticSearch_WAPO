#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue April 20 2021

@author: Xiaoyu Lu
"""
from pathlib import Path
from playhouse.shortcuts import model_to_dict
from peewee import SqliteDatabase, Model  # type: ignore
from peewee import IntegerField, CharField, DateTimeField, TextField  # type: ignore
from typing import Dict, Union, Iterator, List, Any
import os
import json
import nltk
import bisect
from peewee import chunked
from utils import get_word_dict, add_bold, get_seg, normalize_query
import re
# from functools import cache # uncomment it if you are using python3.9
from hyperparas import THRES, THRES_MAX
from collections import defaultdict # needed for eval

data_dir = Path("data")
db_name = "docs50k_whole.db"
db_path = data_dir.joinpath(db_name)
wapo_jl_path = data_dir.joinpath("subset_wapo_50k_sbert_ft_lf_filtered.jl")

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
    words_dict = TextField()


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
                   "content_str": data['content_str'],
                   "words_dict": get_word_dict(data["content_str"])
                   }
            yield val

            idx += 1


# @cache # uncomment it if you are using python 3.9, or change it to lru-cache
def embolden_text(query_text: str, doc_idx: int) -> str:
    """
    Embolden the keywords in query
    :param text:
    :return:
    """
    print(f"Embolden doc {doc_idx}")

    query_tokens = normalize_query(query_text)
    try:
        # database whole, select the word_idx_dict
        doc_dict: Dict[str, Any] = query_doc(doc_idx)
        doc: str = doc_dict["content_str"]
        doc_tokens_basic: List[str] = nltk.word_tokenize(doc)
        words_dict: str = doc_dict["words_dict"]
        word_idx_dict = eval(re.sub(r"<class '(\w+)'>", r'\1', words_dict))
    except:
        raise KeyError

    n = len(doc_tokens_basic)
    seg_idx = word_idx_dict["eos_sign"]
    seg_idx.add(0)  # for computation convenience
    seg_idx.add(n - 1)
    seg_idx = sorted(seg_idx)

    # indices of candidates that can be bold
    res = set()
    for token in query_tokens:
        res = res.union(word_idx_dict[token])
    breakpoints = sorted(res)

    left, right, bos_i, eos_i = get_seg(seg_idx, breakpoints)

    # extract the text tokens from doc tokens
    l = seg_idx[bos_i] + 1 if bos_i else seg_idx[bos_i]  # begins after the end of sentence sign
    r = seg_idx[eos_i] + 1  # including the punc

    if THRES <= r - l < THRES_MAX:  # remain the same
        sent_pieces = doc_tokens_basic[l:r]
        # absolute indices of candidates to be bold
        bold_indices = breakpoints[left:right]
        # get the relative indices of candidates to be bold
        relative_bold_indices = [idx - l for idx in bold_indices]  # - start of sentence index
        return add_bold(sent_pieces, relative_bold_indices)
    elif r - l < THRES:  # add more tokens
        sent_pieces = doc_tokens_basic[l: THRES + l + 1]  # r + (THRES-(r-l))
        right_extend = bisect.bisect_right(breakpoints, THRES + l)
        bold_indices = breakpoints[left:right_extend]
        relative_bold_indices = [idx - l for idx in bold_indices]
        return add_bold(sent_pieces, relative_bold_indices) + " ..."
    else:  # truncate
        sent_pieces = doc_tokens_basic[l:l + THRES_MAX + 1]
        right_shrink = bisect.bisect(breakpoints, l + THRES_MAX)
        bold_indices = breakpoints[left:right_shrink]
        relative_bold_indices = [idx - l for idx in bold_indices]
        return add_bold(sent_pieces, relative_bold_indices) + " ..."


if __name__ == "__main__":
    pass
    # # delete the existed ones before rebuild
    # if db_path.exists():
    #     print("deleting...")
    #     Path(__file__).parent.joinpath(db_path).unlink()
    # df_path_shm = data_dir.joinpath(f"{db_name}-shm")
    # if df_path_shm.exists():
    #     Path(__file__).parent.joinpath().unlink(df_path_shm)
    #     Path(__file__).parent.joinpath(data_dir.joinpath(f"{db_name}-wal")).unlink()
    # print("creating...")
    # create_tables()
    # print("Done...")
    # for i in range(10):
    #     print(query_doc(i))

