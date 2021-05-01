
## load wapo docs into the index called "wapo_docs_50k"
#python load_es_index.py --index_name wapo_docs_50k --wapo_path data/subset_wapo_50k_sbert_ft_filtered.jl

echo "----------------Evalutation 805----------------"
TOPIC_ID=805
python evaluate.py --index_name wapo_docs_50k --topic_id $TOPIC_ID --query_type title --top_k 20
python evaluate.py --index_name wapo_docs_50k --topic_id $TOPIC_ID --query_type title --vector_name ft_vector --top_k 20
python evaluate.py --index_name wapo_docs_50k --topic_id $TOPIC_ID --query_type title --vector_name sbert_vector --top_k 20