from flask import Flask, render_template, request, redirect, session, jsonify
from pymongo import MongoClient
import bcrypt
from your_poker_news_fetcher_module import get_poker_news
from your_poker_odds_api_module import get_poker_odds

app = Flask(__name__, template_folder='templates')
app.secret_key = 'secret'  # [TO-DO] add secretkey_generator.py


# MongoDB configuration
client = MongoClient('mongodb://localhost:27017/')#for development, [TO-DO] add configurations
db = client['database_name']#change later
poker_users = db['poker_users']
sessions = db['sessions']

# Constants
max_presses = 50

# Authentication middleware
def is_authenticated():
    if 'user_id' in session:
        return True
    return False

@app.route('/')
def home():
    if is_authenticated():
        return render_template('pokerMain.html', show_logout_button=True)
    else:
        return render_template('home.html')

@app.route('/pokerMain')
def poker_main():
    if is_authenticated():
        news_items = get_poker_news()
        odds = None
        hand = request.args.get('hand')
        if hand:
            hand = hand.split(',')
            if len(hand) == 2:
                odds = get_poker_odds(hand)
            else:
                odds = {"error": "Invalid hand format. Please enter 2 cards."}
        return render_template('pokerMain.html', username=session['username'], newsItems=news_items, odds=odds)
    else:
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_authenticated():
        return redirect('/')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = poker_users.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['button_press_count'] = user['button_press_count']
            return redirect('/pokerMain')
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_authenticated():
        return redirect('/')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = poker_users.find_one({'username': username})
        if user:
            return render_template('register.html', error='Username already used')
        else:
            poker_users.insert_one({'username': username, 'password': hashed_password, 'button_press_count': 0})
            session['username'] = username
            user = poker_users.find_one({'username': username})
            session['user_id'] = str(user['_id'])
            session['button_press_count'] = user['button_press_count']
            return redirect('/login')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('button_press_count', None)
    return redirect('/login')


@app.route('/getButtonPressCount', methods=['GET'])
def get_button_press_count():
    if is_authenticated():
        return jsonify({'count': session.get('button_press_count', 0)})
    return redirect('/login')

@app.route('/incrementButtonPress', methods=['POST'])
def increment_button_press():
    if is_authenticated():
        try:
            user_id = session.get('user_id')
            user = poker_users.find_one({'_id': ObjectId(user_id)})
            if not user:
                return jsonify({'allowed': False, 'count': 0})
            
            if user['button_press_count'] < max_presses:
                user['button_press_count'] += 1
                poker_users.update_one({'_id': ObjectId(user_id)}, {'$set': {'button_press_count': user['button_press_count']}})
                session['button_press_count'] = user['button_press_count']
                return jsonify({'allowed': True, 'count': user['button_press_count']})
            else:
                return jsonify({'allowed': False, 'count': user['button_press_count']})
        except Exception as e:
            print(f'Error incrementing button press count: {str(e)}')
            return jsonify({'allowed': False, 'count': 0}), 500
    return redirect('/login')

@app.route('/my-sessions')
def my_sessions():
    if is_authenticated():
        user_id = session.get('user_id')
        user_sessions = sessions.find({'user_id': ObjectId(user_id)})
        return render_template('mySessions.html', title="My Sessions", sessions=user_sessions)
    return redirect('/login')


@app.route('/create-session', methods=['GET', 'POST'])
def create_session():
    if is_authenticated():
        if request.method == 'POST':
            # Process and save session data to the database
            # Example: Retrieve data from form and insert into 'sessions' collection
            # session_data = {
            #     'user_id': ObjectId(session.get('user_id')),
            #     'date': request.form.get('date'),
            #     'buyIn': request.form.get('buyIn'),
            #     # Add other session data fields here
            # }
            # sessions.insert_one(session_data)
            return redirect('/my-sessions')
        return render_template('createSession.html', title="Create a Session")
    return redirect('/login')

@app.route('/view-sessions')
def view_sessions():
    if is_authenticated():
        user_id = session.get('user_id')
        user_sessions = sessions.find({'user_id': ObjectId(user_id)})
        return render_template('viewSessions.html', sessions=user_sessions)
    return redirect('/login')

@app.route('/delete-session/<string:session_id>', methods=['POST'])
def delete_session(session_id):
    if is_authenticated():
        user_id = session.get('user_id')
        session_to_delete = sessions.find_one({'_id': ObjectId(session_id), 'user_id': ObjectId(user_id)})
        if session_to_delete:
            sessions.delete_one({'_id': ObjectId(session_id), 'user_id': ObjectId(user_id)})
        return redirect('/view-sessions')
    return redirect('/login')

@app.route('/session-data')
def session_data():
    if is_authenticated():
        # Fetch session data from the 'sessions' collection
        # Example: Retrieve session data for the logged-in user
        # user_id = session.get('user_id')
        # user_sessions = sessions.find({'user_id': ObjectId(user_id)})
        # Process and format the session data as needed
        # Return the formatted data as JSON
        return jsonify({'lineChartData': [], 'histogramData': {}})
    return redirect('/login')

@app.route('/data-analysis')
def data_analysis():
    if is_authenticated():
        return render_template('chartPage.html')


@app.route('/settings')
def user_settings():
    if is_authenticated():
        return render_template('userSettings.html')
    return redirect('/login')

@app.route('/settings/change-password', methods=['GET', 'POST'])
def change_password():
    if is_authenticated():
        if request.method == 'POST':
            # Process and update the user's password in the database
            # Example: Retrieve data from form and update the user's password
            # user_id = session.get('user_id')
            # new_password = request.form.get('new_password')
            # hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            # poker_users.update_one({'_id': ObjectId(user_id)}, {'$set': {'password': hashed_password}})
            return redirect('/settings?success=passwordChanged')
        return render_template('changePassword.html')

@app.route('/settings/change-username', methods=['GET', 'POST'])
def change_username():
    if is_authenticated():
        if request.method == 'POST':
            # Process and update the user's username in the database
            # Example: Retrieve data from form and update the user's username
            # user_id = session.get('user_id')
            # new_username = request.form.get('new_username')
            # poker_users.update_one({'_id': ObjectId(user_id)}, {'$set': {'username': new_username}})
            session['username'] = new_username
            return redirect('/settings?success=usernameChanged')
        return render_template('changeUsername.html')

@app.route('/delete-account', methods=['POST'])
def delete_account():
    if is_authenticated():
        user_id = session.get('user_id')
        poker_users.delete_one({'_id': ObjectId(user_id)})
        sessions.delete_many({'user_id': ObjectId(user_id)})
        session.pop('user_id', None)
        session.pop('username', None)
        session.pop('button_press_count', None)
        return 'Account and associated sessions deleted successfully.'

@app.route('/search', methods=['GET', 'POST'])
def search():
    if is_authenticated():
        if request.method == 'POST':
            # Process and execute the search query
            # Example: Retrieve search parameters from the form and query the database
            # Implement your search logic here
            return render_template('searchResult.html', sessions=found_sessions)
        return render_template('search.html')


@app.route('/search-result', methods=['POST'])
def search_result():
    if is_authenticated() and request.method == 'POST':
        # Process and execute the search query
        # Example: Retrieve search parameters from the form and query the database
        # Implement your search logic here and retrieve the search results
        # Example: found_sessions = sessions.find({ ... })

        # Pass the search results to the template for rendering
        return render_template('searchResult.html', sessions=found_sessions)
    return redirect('/login')



if __name__ == '__main__':
    app.run(debug=True)
