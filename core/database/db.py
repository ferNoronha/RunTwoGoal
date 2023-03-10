from pymongo import mongo_client
from config import settings

client = mongo_client.MongoClient(settings.DATABASE_URL)
print('Connected to MongoDB...')

db = client[settings.MONGO_INITDB_DATABASE]
User_db = db.users
Wallet_db = db.wallet
# Post = db.posts
# User.create_index([("email", pymongo.ASCENDING)], unique=True)
# Post.create_index([("title", pymongo.ASCENDING)], unique=True)
