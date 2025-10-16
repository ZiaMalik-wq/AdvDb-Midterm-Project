import requests
from pymongo import MongoClient

# --- CONFIG ---
API_KEY = "ddcc92f4a9c0c86664bcd37eac9441a2"
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "movie_streaming_db"

# CONNECT TO MONGODB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
movies_col = db.movies

# FETCH GENRE MAPPING
def fetch_genres():
    """Fetch genre ID-to-name mapping from TMDB"""
    url = f"https://api.themoviedb.org/3/genre/movie/list"
    params = {"api_key": API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)
    data = response.json()
    return {g["id"]: g["name"] for g in data.get("genres", [])}

# --- FETCH MOVIES ---
def fetch_movies(page=1):
    """Fetch movies from TMDB (popular list)"""
    url = "https://api.themoviedb.org/3/movie/popular"
    params = {"api_key": API_KEY, "language": "en-US", "page": page}
    response = requests.get(url, params=params)
    return response.json().get("results", [])

# --- FETCH CAST ---
def fetch_cast_and_director(movie_id):
    """Fetch top cast and director name for a given movie"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
    params = {"api_key": API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)
    data = response.json()

    # Take top 5 cast members
    cast_list = []
    for member in data.get("cast", [])[:5]:
        cast_list.append({
            "name": member.get("name"),
            "role": member.get("character")
        })

    # Extract director name
    director = None
    for crew_member in data.get("crew", []):
        if crew_member.get("job") == "Director":
            director = crew_member.get("name")
            break

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

                # Avoid duplicates based on title
                if not movies_col.find_one({"title": movie_doc["title"]}):
                    movies_col.insert_one(movie_doc)
                    total_inserted += 1

            except Exception as e:
                print(f"Error inserting movie {m.get('title')}: {e}")

    print(f"Done! Inserted {total_inserted} new movies.")

if __name__ == "__main__":
    import_movies(num_pages=5)  # 5 pages ≈ ~100 movies
