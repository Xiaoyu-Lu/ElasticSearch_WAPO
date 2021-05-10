import argparse
from collections import defaultdict

from flask import Flask, render_template, request
from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch

from evaluate import get_response, get_score
from db import query_doc
from db805 import embolden_text_805

app = Flask(__name__)
es = Elasticsearch()
DOC_PER_PAGE = 8
K = 20  # less than or equal to: [10000]
INDEX_NAME = "wapo_docs_50k_lf"
DEBUG_TOPIC_ID = 805

storage = defaultdict(dict)  # {query_text: {keyword_text: response}}
connections.create_connection(hosts=["localhost"], timeout=100, alias="default")
show_rel = False    # whether to show doc rel and score on result page



# home page
@app.route("/")
def home():
    return render_template("home.html")


# result page
@app.route("/results", methods=["POST"])
def results():
    global page_num, query_text, option_analyzer, option_embed, keywords_text, score

    query_text = request.form["query"]
    keywords_text = request.form["keywords"]
    if query_text == "" and keywords_text == "":
        return home()

    try:
        option_analyzer = request.form['options_analyzer']
    except:
        option_analyzer = "basic_analyzer"  # default

    try:
        option_embed = request.form['options_embed']
    except:
        option_embed = "bm25"  # default

    print(option_analyzer)
    print(option_embed)
    custom_analyzer = False
    if option_analyzer == "custom_analyzer":
        custom_analyzer = True

    response = get_response(INDEX_NAME, query_text, custom_analyzer, option_embed, K, kw_query=keywords_text)
    storage[query_text][keywords_text] = response
    items = [hit for hit in response[: DOC_PER_PAGE]]

    contents = {hit.meta.id: embolden_text_805(query_text, hit.meta.id) for hit in response[: DOC_PER_PAGE]}
    page_num = (len(response) - 1) // 8 + 1
    score = get_score(response, str(DEBUG_TOPIC_ID), K) if show_rel else None

    return render_template("results.html", items_list=items, ids_list=response, page_id=1, page_num=page_num,
                           query_text=query_text, kw_text=keywords_text,
                           hits_num=len(response), start=1, DOC_PER_PAGE=DOC_PER_PAGE, option_analyzer=option_analyzer,
                           option_embed=option_embed, contents=contents, show_rel=show_rel, score=score)


# "next page" to show more results
@app.route("/results/<int:page_id>", methods=["POST"])
def next_page(page_id):
    response = storage[query_text][keywords_text]  # Get the response from dict - the storage
    items = [hit for hit in response[(page_id - 1) * DOC_PER_PAGE: page_id * DOC_PER_PAGE]]
    contents = {hit.meta.id: embolden_text_805(query_text, hit.meta.id) for hit in
                response[(page_id - 1) * DOC_PER_PAGE: page_id * DOC_PER_PAGE]}

    return render_template("results.html", items_list=items, ids_list=response, page_id=page_id, page_num=page_num,
                           query_text=query_text, hits_num=len(response), start=(page_id - 1) * DOC_PER_PAGE + 1,
                           DOC_PER_PAGE=DOC_PER_PAGE, option_analyzer=option_analyzer, option_embed=option_embed,
                           contents=contents, show_rel=show_rel, score=score)


# document page
@app.route("/doc_data/<int:doc_id>")
def doc_data(doc_id):
    print(doc_id)
    doc = query_doc(doc_id)
    return render_template("doc.html", doc=doc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Name of Program",
                                     description="Program Description")
    parser.add_argument("--debug",
                        action="store_true",
                        help="If selected, result page shows annotation and evaluation scores")
    args = parser.parse_args()

    show_rel = args.debug

    app.run(debug=True, port=5000)
