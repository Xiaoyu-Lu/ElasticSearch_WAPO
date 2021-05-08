from flask import Flask, render_template, request
from evaluate import get_response
from elasticsearch_dsl.connections import connections
from db import query_doc
from elasticsearch import Elasticsearch

es = Elasticsearch()
app = Flask(__name__)
DOC_PER_PAGE = 8
K = 20  # less than or equal to: [10000]
INDEX_NAME = "wapo_docs_50k"
storage = {}  # {query_text: response}
connections.create_connection(hosts=["localhost"], timeout=100, alias="default")


# home page
@app.route("/")
def home():
    return render_template("home.html")


# result page
@app.route("/results", methods=["POST"])
def results():
    global page_num, query_text, option_analyzer, option_embed

    query_text = request.form["query"]
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

    response = get_response(INDEX_NAME, query_text, custom_analyzer, option_embed, K)
    storage[query_text] = response
    items = [hit for hit in response[: DOC_PER_PAGE]]
    page_num = (len(response) - 1) // 8 + 1

    ids_list = [hit.meta.id for hit in response]

    return render_template("results.html", items_list=items, ids_list=ids_list, page_id=1, page_num=page_num,
                           query_text=query_text,
                           hits_num=len(response), start=1, DOC_PER_PAGE=DOC_PER_PAGE, option_analyzer=option_analyzer,
                           option_embed=option_embed)


# "next page" to show more results
@app.route("/results/<int:page_id>", methods=["POST"])
def next_page(page_id):
    print(page_id)
    # query_text = request.form["query"]
    # option_analyzer = request.form['options_analyzer']
    # option_embed = request.form['options_embed']
    response = storage[query_text]  # Get the response from dict - the storage
    items = [hit for hit in response[(page_id - 1) * DOC_PER_PAGE: page_id * DOC_PER_PAGE]]
    ids_list = [hit.meta.id for hit in response]

    return render_template("results.html", items_list=items, ids_list=ids_list, page_id=page_id, page_num=page_num,
                           query_text=query_text, hits_num=len(response), start=(page_id - 1) * DOC_PER_PAGE + 1,
                           DOC_PER_PAGE=DOC_PER_PAGE, option_analyzer=option_analyzer, option_embed=option_embed)


# document page
@app.route("/doc_data/<int:doc_id>")
def doc_data(doc_id):
    doc = es.get_source('wapo_docs_50k', doc_id)
    # doc = query_doc(doc_id)  # Get the doc from db
    return render_template("doc.html", doc=doc)


if __name__ == "__main__":
    app.run(debug=True, port=5000)