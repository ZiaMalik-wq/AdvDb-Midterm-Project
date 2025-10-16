from flask import Flask
from config import MONGO_URI
from db import mongo
from flask import Blueprint, request, jsonify
from utils.similarity_search import search_similar_movies

app = Flask(__name__)
app.config["MONGO_URI"] = MONGO_URI

# initialize mongo with app
mongo.init_app(app)

# Import and register Blueprints
from routes.users import users_bp
from routes.movies import movies_bp
from routes.reviews import reviews_bp

app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(movies_bp, url_prefix="/movies")
app.register_blueprint(reviews_bp, url_prefix="/movies")

# Root endpoint
@app.route("/")
def home():
    return {
        "message": "🎬 Welcome to the Movie Streaming Backend API!",
        "endpoints": {
            "User History": "/users/<user_id>/history",
            "Movie Reviews": "/movies/<movie_id>/reviews",
            "Search": "/movies/search?query=<keyword>"
        },
        "status": "running"
    }

if __name__ == "__main__":
    app.run(debug=True)
