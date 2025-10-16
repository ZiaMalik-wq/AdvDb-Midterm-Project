from flask import Blueprint, jsonify
from bson import ObjectId
from db import mongo

# Create a Blueprint for review-related routes
reviews_bp = Blueprint("reviews_bp", __name__)

# Purpose: Fetch all reviews for a specific movie
@reviews_bp.route("/<movie_id>/reviews", methods=["GET"])
def get_movie_reviews(movie_id):
    """
    Fetch all reviews of a given movie from MongoDB.
    Each review includes rating, review text, user, and timestamp.
    """

    try:
        movie_obj_id = ObjectId(movie_id)

        # Find all reviews for the movie
        review_docs = list(mongo.db.reviews.find({"movie_id": movie_obj_id}))

        # Convert ObjectIds for JSON response
        for doc in review_docs:
            doc["_id"] = str(doc["_id"])
            doc["movie_id"] = str(doc["movie_id"])
            doc["user_id"] = str(doc["user_id"])

        return jsonify({
            "status": "success",
            "count": len(review_docs),
            "reviews": review_docs
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
