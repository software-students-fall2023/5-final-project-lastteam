# db.py
from pymongo import MongoClient
from dbConfig import DB_URI, DB_NAME

client = MongoClient(DB_URI)
db = client[DB_NAME]
