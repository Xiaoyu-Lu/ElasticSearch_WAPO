# ElasticSearch_WAPO
COSI 132a Final Project

Team members: Yonglin Wang,  Xiaoyu Lu, Yun-jing Lee, Ruobin Hu


## How to Run the Code
### 1. Activate Environment
*Remember to always activate your virtual environment first.*

### 2. First-time Running
Run the following subsections only once, when you set up the project for the first time.
#### 2.1 Install Dependencies
```
$ pip install -r requirements.txt
```
#### 2.2 Setting up ElasticSearch Server

After you install elasticsearch-dsl-py package, add the following code at the end of `elasticsearch_dsl/query.py`:
```python
class ScriptScore(Query):
    name = "script_score"
    _param_defs = {"query": {"type": "query"}}
```
Download ES from https://www.elastic.co/downloads/past-releases#elasticsearch. Make sure you are choosing Elasticsearch 7.10.2 (used for scoring the assignment). To start the ES engine:

```shell
$ cd elasticsearch-7.10.2/
$ ./bin/elasticsearch
```

#### 2.3 Build Index

```shell
# load wapo docs into the index called "wapo_docs_50k_lf"
$ python load_es_index.py --index_name wapo_docs_50k_lf --wapo_path data/subset_wapo_50k_sbert_ft_lf_filtered.jl
```

#### 2.4 Download Database

You need to click [here](https://drive.google.com/uc?export=download&id=1lfXuiI4oMj37p0_hbzS593LoQuy9zoZp) to download the prebuilt database first. 

Or you can create the database by running  `$ python db.py ` to get a tast of the time it takes (~1 hour) to build db from all documents.

​	- Make sure the code under ```if __name__=="__main__":``` in  [db.py](db.py) is all uncommented before creating databases.

### 3. Setting up ElasticSearch Server
If you haven't done so already, run the following command to start an ES server:
```shell script
cd elasticsearch-7.10.2/
./bin/elasticsearch
```

### 4. Setting up Embedding Servers

You don’t need to download any pretrained model for sentence transformers, it will be loaded the first time it's called.

- Load fasttext model (click [this](https://dl.fbaipublicfiles.com/fasttext/vectors-english/wiki-news-300d-1M-subword.vec.zip) link to download `.vec` file first,  then put it into `data/` folder):

```shell script
python -m embedding_service.server --embedding fasttext  --model data/wiki-news-300d-1M-subword.vec
```

- Load sbert model:

```shell script
python -m embedding_service.server --embedding sbert --model msmarco-distilbert-base-v3
```

- Load longformer model (download for the first time):

```shell script
python -m embedding_service.server --embedding longformer --model allenai/longformer-base-4096
```


### 5. Running the Programs

- For Evaluation: 
    Change ```TOPIC_ID``` to the topic ID you want to evaluate.
    ```shell
    $ sh scirpts.sh
    ```

- For web app:

    Run the app, then type http://127.0.0.1:5000/ in the browser to view the web application.
    
    ```shell script
    python app.py 
    ```
    If you'd like to see scores for Topic 805 and annotations on the result page, run
    ```shell script
    python app.py --debug 
    ```

## How to Search
Our BM25 retrieval system defaults to using keyword text and falls back to query text if no keyword text is provided. If neither keyword nor query text is provided, the program will jump back to home page.

Reranking will only be performed if query text is provided and reranking is based on query text only. 
### Case 1: Using both Query and Keywords
The top K results will be retrieved based on the keyword text and, if reranking, reranked based on the query text.
### Case 2: Using Query Text Only
The top K results will be retrieved based on the query text and, if reranking, reranked based on the query text as well.

This is the default behavior in PA5. 
### Case 3: Using Keywords Only
The top K results will be retrieved based on the keyword text. 

Intuitively, no reranking will be performed even if a reranking method is specified. This means that if a user searches with only keywords and chooses fastText as the reranking method, the system will correct the reranking method to BM25 only (i.e. no reranking). 

