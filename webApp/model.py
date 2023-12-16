# models.py

from db import db
from bson import ObjectId

# User Structure
def create_user(username, password, email):
    user = {
        "username": username,
        "password": password,  # Ensure this is hashed
        "email": email,
        "buttonPressCount": 0,
        "sessions": []
    }
    return db.poker_users.insert_one(user).inserted_id

# Session Structure
def create_session(user_id, date, buyIn, cashOut, highlights, location):
    session = {
        "user": ObjectId(user_id),
        "date": date,
        "buyIn": buyIn,
        "cashOut": cashOut,
        "profit": cashOut - buyIn,
        "highlights": highlights,
        "location": location
    }
    return db.sessions.insert_one(session).inserted_id


