# Longformer Embedding Instructions

Author: Yonglin Wang

This file will load a pretrained Longformer from hugging face, vectorize the documents (sentence truncated to <= 4096 word bits).

## Package Requirement

Install the following packages

- Python 3.7
- PyTorch 1.8.1: ```pip install torch```
- Sentence Tranformers 4.5.1: ```pip install transformers```

## Command line usage

### Downloading Model and Tokenizer

To download the model and tokenizer, open a Python shell on the machine you're running the script, and run the following example code adapted from [the example section of the original model](https://huggingface.co/transformers/model_doc/longformer.html#transformers.LongformerModel).

```python
import torch
from transformers import LongformerModel, LongformerTokenizer
model = LongformerModel.from_pretrained('allenai/longformer-base-4096')
tokenizer = LongformerTokenizer.from_pretrained('allenai/longformer-base-4096')
```

### GPU Command

**GPU** is highly recommended for running this script. It took ~7 hours to encode all of the documents in the subset. 

To use the script on GPU, use the following command, where the first file path is to the original wapo files that minimally contains content string and content id, and the second file path will be where the new .jl file with Longformer encoding is saved. 

```shell script
TRANSFORMERS_OFFLINE=1 python longformer.py subset_wapo_50k_sbert_ft_filtered.jl \
                                            subset_wapo_50k_sbert_ft_lf_filtered.jl
```

### CPU Command

If you'd like to try the code on CPU, you can take of the ```TRANSFORMERS_OFFLINE``` variable and start with the python command.

```shell script
python longformer.py subset_wapo_50k_sbert_ft_filtered.jl \
                     subset_wapo_50k_sbert_ft_lf_filtered.jl
```

## Incorporating Longformer Embeddings in ElasticSearch

To incorporate Longformer in our project so that ES can run semantic search using Longformer document vectors and that queries can be encoded using longformer as well, we modified the following files (based on PA5 code). 

1. [embed.py](../embedding_service/embed.py) to add the code for Longformer class in [longformer.py](longformer.py)
2. [doc_template.py](../es_service/doc_template.py) to add the 768-dimensional lf vector to the document template
3. [index.py](../es_service/index.py) to add ```es_doc.lf_vector = doc["lf_vector"]```
4. [app.py](../app.py) and [evaluate.py](../evaluate.py) for any additional logical statements
