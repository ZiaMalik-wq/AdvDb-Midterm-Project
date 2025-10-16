from faker import Faker
from pymongo import MongoClient
import random

fake = Faker()

# -----------------------
# 0️⃣ MongoDB Connection
# -----------------------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "movie_streaming_db"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# -----------------------
# 1️⃣ Insert Users
# -----------------------
users = []
subscription_types = ["Free", "Standard", "Premium"]

for _ in range(15):  # 15 users
    users.append({
        "name": fake.name(),
        "email": fake.email(),
        "subscription_type": random.choice(subscription_types)
    })

db.users.insert_many(users)
print(f"✅ Inserted {len(users)} users")

# -----------------------
# 2️⃣ Check Movies Collection
# -----------------------
movies = list(db.movies.find())
if not movies:
    print("⚠️ No movies found. Please run your TMDB import script first!")
else:
    print(f"🎬 Found {len(movies)} movies in database.")

# -----------------------
# 3️⃣ Insert Reviews
# -----------------------
reviews = []
for _ in range(80):  # total reviews
    movie = random.choice(movies)
    user = random.choice(list(db.users.find()))
    reviews.append({
        "user_id": user["_id"],
        "movie_id": movie["_id"],
        "rating": random.randint(1, 10),
        "review_text": fake.sentence(nb_words=12),
        "timestamp": fake.date_time_this_year().isoformat()
    })

db.reviews.insert_many(reviews)
print(f"✅ Inserted {len(reviews)} reviews")

# -----------------------
# 4️⃣ Insert Watch History
# -----------------------
watch_history = []
for _ in range(150):  # total watch records
    movie = random.choice(movies)
    user = random.choice(list(db.users.find()))
    watch_history.append({
        "user_id": user["_id"],
        "movie_id": movie["_id"],
        "timestamp": fake.date_time_this_year().isoformat(),
        "watch_duration": random.randint(30, 180)  # duration in minutes
    })

db.watch_history.insert_many(watch_history)
print(f"✅ Inserted {len(watch_history)} watch history records")

print("🎉 Database seeding complete!")
