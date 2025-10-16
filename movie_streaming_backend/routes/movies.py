from flask import Blueprint, request, jsonify
from db import mongo
from utils.similarity_search import search_similar_movies

# Blueprint for movie routes
movies_bp = Blueprint("movies_bp", __name__)

# Search movies by title, genre, or director
@movies_bp.route("/search_regex", methods=["GET"])
def search_movies_regex():
    """
    Search movies in the database by keyword.
    The keyword will be matched against title, genre, and director.
    """
    try:
        query = request.args.get("query", "").strip()

        if not query:
            return jsonify({"status": "error", "message": "Please provide a search query"}), 400

        # Perform a case-insensitive search in MongoDB
        search_results = list(
            mongo.db.movies.find({
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"genres": {"$elemMatch": {"$regex": query, "$options": "i"}}},
                    {"director": {"$regex": query, "$options": "i"}},
                    {"cast.name": {"$regex": query, "$options": "i"}}
                ]
            })
        )

        # Convert ObjectIds to strings
        for movie in search_results:
            movie["_id"] = str(movie["_id"])

        return jsonify({
            "status": "success",
            "count": len(search_results),
            "results": search_results
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@movies_bp.route("/search", methods=["GET"])
def search_movies():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"status": "error", "message": "Please provide a query"}), 400

    results = search_similar_movies(query)
    return jsonify({
        "status": "success",
        "count": len(results),
        "results": results
    })