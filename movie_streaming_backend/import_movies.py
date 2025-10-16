import os
from dotenv import load_dotenv
import requests
from pymongo import MongoClient

# --- LOAD ENV ---
load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# CONNECT TO MONGODB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
movies_col = db.movies

# FETCH GENRES
def fetch_genres():
    url = "https://api.themoviedb.org/3/genre/movie/list"
    params = {"api_key": API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)
    data = response.json()
    return {g["id"]: g["name"] for g in data.get("genres", [])}

# FETCH MOVIES
def fetch_movies(page=1):
    url = "https://api.themoviedb.org/3/movie/popular"
    params = {"api_key": API_KEY, "language": "en-US", "page": page}
    response = requests.get(url, params=params)
    return response.json().get("results", [])

# FETCH CAST
def fetch_cast_and_director(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
    params = {"api_key": API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)
    data = response.json()

    cast_list = [{"name": m.get("name"), "role": m.get("character")} for m in data.get("cast", [])[:5]]

    director = next((c["name"] for c in data.get("crew", []) if c.get("job") == "Director"), None)

    return cast_list, director

def import_movies(num_pages=5):
    genres_map = fetch_genres()
    total_inserted = 0

    for page in range(1, num_pages + 1):
        print(f"Fetching page {page}...")
        movies = fetch_movies(page)
        for m in movies:
            try:
                cast, director = fetch_cast_and_director(m["id"])
                movie_doc = {
                    "title": m.get("title"),
                    "release_year": int(m.get("release_date", "0000")[:4]) if m.get("release_date") else None,
                    "genres": [genres_map.get(g) for g in m.get("genre_ids", []) if g in genres_map],
                    "cast": cast,
                    "director": director,
                    "average_rating": round(m.get("vote_average", 0), 1),
                    "watch_count": int(m.get("popularity", 0)),
                    "overview": m.get("overview", "")
                }

                if not movies_col.find_one({"title": movie_doc["title"]}):
                    movies_col.insert_one(movie_doc)
                    total_inserted += 1
            except Exception as e:
                print(f"Error inserting movie {m.get('title')}: {e}")

    print(f"Done! Inserted {total_inserted} new movies.")

if __name__ == "__main__":
    import_movies(num_pages=5)
