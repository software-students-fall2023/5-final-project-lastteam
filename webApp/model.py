# models.py

from db import db
from bson import ObjectId


# User Structure
def create_user(username, password, email):
    user = {
        "username": username,
        "password": password,
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


# Function to get sessions for a specific user

# we query the user_id to retrieve the specific session(s) for the user instead of updating it each time
def get_sessions_for_user(user_id):
    """
    Retrieve all sessions for a given user.

    :param user_id: The ObjectId of the user.
    :return: List of session documents.
    """
    return list(db.sessions.find({"user": ObjectId(user_id)}))


# Find User
def find_user(username):
    return db.poker_users.find_one({"username": username})


# Delete User
def delete_user(user_id):
    db.poker_users.delete_one({"_id": ObjectId(user_id)})
    # Optionally, delete related sessions
    db.sessions.delete_many({"user": ObjectId(user_id)})


# Update User
def update_user(user_id, update_data):
    db.poker_users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
