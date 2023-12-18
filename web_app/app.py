"""Web App"""
from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session

app = Flask(__name__)

sess = Session()

client = pymongo.MongoClient("db", 27017)
db = client["testdb"]

try:
    client.admin.command("ping")
    print(" *", "Connected to MongoDB!")
except ConnectionError as e:
    print(" * MongoDB connection error:", e)


@app.route("/")
def home():
    """Route for home page"""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Route for login page"""
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = db["users"].find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            return redirect(url_for("home"))
        else:
            error = "Login credential not correct!"
            return render_template("login.html", error=error)

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Route for register page"""
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if db["users"].find_one({"username": username}):
            error = "Username already exists!"
            return render_template("register.html", error=error)

        hashed_password = generate_password_hash(password)

        db["users"].insert_one(
            {
                "username": username,
                "password": hashed_password,
            }
        )

        return redirect(url_for("home"))

    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5001)
