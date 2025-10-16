import torch
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient


# MongoDB setup
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "movie_streaming_db"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Load movies with embeddings
movies = list(db.movies.find({"embedding": {"$exists": True}}))
if not movies:
    raise Exception("No movies with embeddings found in MongoDB")

# Convert embeddings to torch tensor
movie_embeddings = torch.tensor([movie["embedding"] for movie in movies])

# Load model
model = SentenceTransformer('all-MiniLM-L12-v2')

# Similarity search function
def search_similar_movies(query, top_k=5):
    """
    Returns top_k movies similar to the query.
    """
    query_emb = torch.tensor(model.encode([query]))
    cos_scores = torch.nn.functional.cosine_similarity(query_emb, movie_embeddings)
    top_results = torch.topk(cos_scores, k=top_k)

    results = []
    for score, idx in zip(top_results.values, top_results.indices):
        movie = movies[idx]
        results.append({
            "movie_id": str(movie["_id"]),
            "title": movie["title"],
            "score": float(score),
            "average_rating": movie.get("average_rating", 0),
            "watch_count": movie.get("watch_count", 0)
        })

    return results
