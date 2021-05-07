# ElasticSearch_WAPO
COSI 132a Final Project

Team members: Yonglin Wang,  Xiaoyu Lu, Yun-jing Lee, Ruobin Hu



**Dependencies**: 

```
$ pip install -r requirements.txt
```

Download ES from https://www.elastic.co/downloads/past-releases#elasticsearch. Make sure you are choosing Elasticsearch 7.10.2 (used for scoring the assignment). To start the ES engine:

```shell
$ cd elasticsearch-7.10.2/
$ ./bin/elasticsearch
```

**Preparation:**
You need to download the pretrained fastText embedding on wiki news and put it into data/ folder. You can click [this](https://dl.fbaipublicfiles.com/fasttext/vectors-english/wiki-news-300d-1M-subword.vec.zip) link to download. You don’t need to download any pretrained model for sentence transformers, it will be loaded the first time it's called.

load fasttext model (download):

```shell
$ python -m embedding_service.server --embedding fasttext  --model data/wiki-news-300d-1M-subword.vec
```

load sbert model:

```shell
$ python -m embedding_service.server --embedding sbert --model msmarco-distilbert-base-v3
```

load longformer model:

```shell
python -m embedding_service.server --embedding longformer --model allenai/longformer-base-4096
```

Create wapo database from .jl file:

```shell
$ python db.py 
```

**Run Instructions**: 

- Build Index:

```shell
# load wapo docs into the index called "wapo_docs_50k"
$ python load_es_index.py --index_name wapo_docs_50k --wapo_path data/subset_wapo_50k_sbert_ft_lf_filtered.jl
```

- For Evaluation: 

```shell
$ sh scirpts.sh
```

- For web app:

Run the app,  then type http://127.0.0.1:5000/ in the browser to view the web application.

```shell
$ python app.py 
```

