# nlp_model.py
from sentence_transformers import SentenceTransformer

# Light model suitable for local use
model = SentenceTransformer("all-MiniLM-L6-v2")
