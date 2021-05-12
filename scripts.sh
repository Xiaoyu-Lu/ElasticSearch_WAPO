# load fasttext embeddings that are trained on wiki news. Each embedding has 300 dimensions
#python -m embedding_service.server --embedding fasttext --model data/wiki-news-300d-1M-subword.vec

# load sentence BERT embeddings that are trained on msmarco. Each embedding has 768 dimensions
#python -m embedding_service.server --embedding sbert --model msmarco-distilbert-base-v3

# load sentence longformer embeddings that are trained on 'allenai/longformer-base-4096'. Each embedding has 768 dimensions
#python -m embedding_service.server --embedding longformer --model allenai/longformer-base-4096

## load wapo docs into the index called "wapo_docs_50k_lf"
#python load_es_index.py --index_name wapo_docs_50k_lf --wapo_path data/subset_wapo_50k_sbert_ft_lf_filtered.jl
# python load_es_index.py --rewrite --index_name wapo_docs_50k_lf --wapo_path data/subset_wapo_50k_sbert_ft_lf_filtered.jl |tee -a output.txt
TOPIC_ID=805
index_name="wapo_docs_50k_lf"
#echo "----------------Evalutation $TOPIC_ID----------------"
python evaluate.py --index_name $index_name --topic_id $TOPIC_ID --query_type title --top_k 20
python evaluate.py --index_name $index_name --topic_id $TOPIC_ID --query_type title --vector_name ft_vector --top_k 20
python evaluate.py --index_name $index_name --topic_id $TOPIC_ID --query_type title --vector_name sbert_vector --top_k 20
python evaluate.py --index_name $index_name --topic_id $TOPIC_ID --query_type title --vector_name lf_vector --top_k 20