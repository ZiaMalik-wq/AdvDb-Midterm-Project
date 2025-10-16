from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

# MongoDB setup
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "movie_streaming_db"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

movies = list(db.movies.find({}))
if not movies:
    print("No movies found in MongoDB 'movies' collection")
    exit()

# Load embedding model
model = SentenceTransformer('all-MiniLM-L12-v2')
print("Model loaded")


# Compute and store embeddings
for movie in movies:
    title = movie['title']
    emb = model.encode([title])[0].tolist()  # convert to list for MongoDB
    db.movies.update_one(
        {"_id": movie["_id"]},
        {"$set": {"embedding": emb}}
    )

print(f"Stored embeddings for {len(movies)} movies")
