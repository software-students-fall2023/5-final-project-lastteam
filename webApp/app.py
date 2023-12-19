from flask import Flask, render_template, request, redirect, session, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt

from pokerNewsFetcher import get_poker_news

# from your_poker_odds_api_module import get_poker_odds

app = Flask(__name__, template_folder="templates")
app.secret_key = "secret"  # [TO-DO] add secretkey_generator.py

# MongoDB configuration
client = MongoClient("db", 27017)  # for development, [TO-DO] add configurations
db = client["database_name"]  # change later
poker_users = db["poker_users"]
sessions = db["sessions"]

# Constants
max_presses = 50


# Authentication middleware
def is_authenticated():
    if "user_id" in session:
        return True
    return False


@app.route("/")
def home():
    if is_authenticated():
        # return render_template("pokerMain.html", show_logout_button=True)
        return render_template("pokerMain.html", username=session["username"])

    return render_template("home.html")


@app.route("/pokerMain")
def poker_main():
    if is_authenticated():
        try:
            news_items = get_poker_news()
            print(news_items)
        except Exception as e:
            news_items = []
            error_message = "Error fetching poker news."
            # Optionally, handle the error more gracefully, perhaps logging it or informing the user

        # odds = None
        # hand = request.args.get("hand")
        # if hand:
        #     hand = hand.split(",")
        #     if len(hand) == 2:
        #         odds = get_poker_odds(hand)
        #     else:
        #         odds = {"error": "Invalid hand format. Please enter 2 cards."}
        # return render_template(
        #     "pokerMain.html",
        #     username=session["username"],
        #     newsItems=news_items,
        #     odds=odds,
        # )
        return render_template("pokerMain.html", newsItems=news_items, username=session["username"],
                               error=error_message if 'error_message' in locals() else None)

    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Route for login page"""
    if is_authenticated():
        return redirect("/")

    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = poker_users.find_one({"username": username})

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            session["button_press_count"] = user["button_press_count"]
            return redirect("/pokerMain")

        error = "Invalid username or password!"
        return render_template("login.html", error=error)

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Route for register page"""
    if is_authenticated():
        return redirect("/")

    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if poker_users.find_one({"username": username}):
            error = "Username already exists!"
            return render_template("register.html", error=error)

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        poker_users.insert_one(
            {
                "username": username,
                "password": hashed_password,
                "button_press_count": 0,
            }
        )

        session["username"] = username
        user = poker_users.find_one({"username": username})
        session["user_id"] = str(user["_id"])
        session["button_press_count"] = user["button_press_count"]

        return redirect("/pokerMain")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("button_press_count", None)
    return redirect("/login")


@app.route("/getButtonPressCount", methods=["GET"])
def get_button_press_count():
    if is_authenticated():
        return jsonify({"count": session.get("button_press_count", 0)})
    return redirect("/login")


@app.route("/incrementButtonPress", methods=["POST"])
def increment_button_press():
    if is_authenticated():
        try:
            user_id = session.get("user_id")
            user = poker_users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return jsonify({"allowed": False, "count": 0})

            if user["button_press_count"] < max_presses:
                user["button_press_count"] += 1
                poker_users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"button_press_count": user["button_press_count"]}},
                )
                session["button_press_count"] = user["button_press_count"]
                return jsonify({"allowed": True, "count": user["button_press_count"]})
            else:
                return jsonify({"allowed": False, "count": user["button_press_count"]})
        except Exception as e:
            print(f"Error incrementing button press count: {str(e)}")
            return jsonify({"allowed": False, "count": 0}), 500
    return redirect("/login")


@app.route("/my-sessions")
def my_sessions():
    if is_authenticated():
        user_id = session.get("user_id")
        user_sessions = sessions.find({"user_id": ObjectId(user_id)})
        return render_template(
            "mySessions.html", title="My Sessions", sessions=user_sessions
        )
    return redirect("/login")


@app.route("/create-session", methods=["GET", "POST"])
def create_session():
    if not is_authenticated():
        return redirect("/login")

    if request.method == "POST":
        session_data = {
            "user_id": ObjectId(session.get("user_id")),
            "date": request.form.get("date"),
            "buyIn": request.form.get("buyIn"),
            "cashOut": request.form.get("cashOut"),
        }
        sessions.insert_one(session_data)
        return redirect("/my-sessions")

    return render_template("createSession.html")


@app.route("/view-sessions")
def view_sessions():
    if is_authenticated():
        user_id = session.get("user_id")
        user_sessions = sessions.find({"user_id": ObjectId(user_id)})
        return render_template("viewSessions.html", sessions=user_sessions)
    return redirect("/login")


@app.route("/delete-session/<string:session_id>", methods=["POST"])
def delete_session(session_id):
    if is_authenticated():
        user_id = session.get("user_id")
        session_to_delete = sessions.find_one(
            {"_id": ObjectId(session_id), "user_id": ObjectId(user_id)}
        )
        if session_to_delete:
            sessions.delete_one(
                {"_id": ObjectId(session_id), "user_id": ObjectId(user_id)}
            )
        return redirect("/view-sessions")
    return redirect("/login")


@app.route("/session-data")
def session_data():
    if not is_authenticated():
        return redirect("/login")

    user_id = session.get("user_id")
    user_sessions = sessions.find({"user_id": ObjectId(user_id)})
    # Process and format the session data as needed
    # Return the formatted data as JSON
    return jsonify({"sessions": list(user_sessions)})


from bson.json_util import dumps
from datetime import datetime


@app.route("/data-analysis")
def data_analysis():
    if is_authenticated():
        user_id = sessions.get("user_id")

        # Fetch sessions and process the data for charts
        user_sessions = sessions.find({"user_id": ObjectId(user_id)})

        # Prepare data for line chart (profit over time)
        line_chart_data = [
            {'date': session['date'], 'profit': session['cashOut'] - session['buyIn']}
            for session in user_sessions
        ]

        # Prepare data for histogram (monthly profit)
        histogram_data = {}
        for session in user_sessions:
            month = datetime.strptime(session['date'], "%Y-%m-%d").strftime("%b")
            profit = session['cashOut'] - session['buyIn']
            histogram_data[month] = histogram_data.get(month, 0) + profit

        return render_template("chartPage.html",
                               line_chart_data=dumps(line_chart_data),
                               histogram_data=dumps(histogram_data))


@app.route("/settings")
def user_settings():
    if is_authenticated():
        return render_template("userSettings.html")
    return redirect("/login")


@app.route("/settings/change-password", methods=["GET", "POST"])
def change_password():
    if not is_authenticated():
        return redirect("/login")

    if request.method == "POST":
        current_password = request.form.get("currentPassword")
        new_password = request.form.get("newPassword")
        user_id = session.get("user_id")

        user = poker_users.find_one({"_id": ObjectId(user_id)})
        if user and bcrypt.checkpw(current_password.encode('utf-8'), user['password']):
            hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
            poker_users.update_one({"_id": ObjectId(user_id)}, {"$set": {"password": hashed_password}})
            return redirect("/settings?success=passwordChanged")
        else:
            error = "Current password is incorrect!"
            return render_template("changePassword.html", error=error)

    return render_template("changePassword.html")


@app.route("/settings/change-username", methods=["GET", "POST"])
def change_username():
    if not is_authenticated():
        return redirect("/login")

    if request.method == "POST":
        new_username = request.form.get("newUsername")
        user_id = session.get("user_id")

        if poker_users.find_one({"username": new_username}):
            return render_template("changeUsername.html", error="Username already exists!")

        poker_users.update_one({"_id": ObjectId(user_id)}, {"$set": {"username": new_username}})
        session["username"] = new_username

        return redirect("/settings?success=usernameChanged")

    return render_template("changeUsername.html")


@app.route("/delete-account", methods=["POST"])
def delete_account():
    if is_authenticated():
        user_id = session.get("user_id")
        poker_users.delete_one({"_id": ObjectId(user_id)})
        sessions.delete_many({"user_id": ObjectId(user_id)})
        session.pop("user_id", None)
        session.pop("username", None)
        session.pop("button_press_count", None)
        return "Account and associated sessions deleted successfully."


@app.route("/search", methods=["GET", "POST"])
def search():
    if not is_authenticated():
        return redirect("/login")

    if request.method == "POST":
        search_query = request.form.get("search_query")
        return redirect(url_for("search_result", query=search_query))

    return render_template("search.html")


@app.route("/search-result", methods=["POST"])
def search_result():
    if not is_authenticated():
        return redirect("/login")

    # Retrieve form data
    date = request.form.get("date")
    buy_in = request.form.get("buyIn")
    location = request.form.get("location")
    profit_loss_selection = request.form.get("profitLossSelection")

    # Build query based on form data
    query = {}
    if date:
        query["date"] = date
    if buy_in:
        query["buyIn"] = float(buy_in)
    if location:
        query["location"] = location
    if profit_loss_selection:
        if profit_loss_selection == "profit":
            query["profit"] = {"$gt": 0}
        elif profit_loss_selection == "loss":
            query["profit"] = {"$lt": 0}

    # Perform the search
    found_sessions = sessions.find(query)

    return render_template("searchResult.html", sessions=list(found_sessions))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
