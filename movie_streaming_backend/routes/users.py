from flask import Blueprint, jsonify
from bson import ObjectId
from db import mongo

users_bp = Blueprint("users_bp", __name__)

@users_bp.route("/<user_id>/history", methods=["GET"])
def get_watch_history(user_id):
    try:
        user_obj_id = ObjectId(user_id)
        history_docs = list(mongo.db.watch_history.find({"user_id": user_obj_id}))

        for doc in history_docs:
            doc["_id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
            doc["movie_id"] = str(doc["movie_id"])

        return jsonify({
            "status": "success",
            "count": len(history_docs),
            "history": history_docs
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
