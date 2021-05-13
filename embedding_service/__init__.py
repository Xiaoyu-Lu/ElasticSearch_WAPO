"""
@modified by: Yunjing Lee
"""
# set the port number for an embedding server
# we may want to be consistent about the port number for different servers to avoid conflicts.
PORT_EMBEDDING_MAPPING = {8080: "sbert", 8081: "fasttext", 8082: "longformer"}
INV_PORT_EMBEDDING_MAPPING = {"sbert": 8080, "fasttext": 8081, "longformer": 8082}
