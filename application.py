import os
import csv
import random
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, get_question, get_compatible_pokemon


# flask --app application run
#test

# Configure application
app = Flask(__name__)
app.secret_key = 'fix dit later'

# Initialize Flask-SocketIO
socketio = SocketIO(app)

room_list = {}
room_guess_scores = {}
room_point_scores = {}
room_progress = {}

pokemon_dict = {}
with open('resources/pokemon_properties.csv', mode='r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for idx, row in enumerate(reader):
        pokemon_dict[idx] = {
            'number': int(row['number']),
            'name': row['name'],
            'type1': row['type1'],
            'type2': row['type2'],
            'region': row['region'],
            'stage': int(row['stage'])
        }


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///pokequiz.db")

connected_users = {}

@app.route("/")
def index():
    """Show portfolio of stocks"""

    return render_template("index.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        return render_template("bought.html")

    else:
        return render_template("buy.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure the password and confirmation match
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("password and confirmation don't match", 400)


        # Defineer de username en password
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if the username is taken
        usernames = db.execute("SELECT username FROM users")
        usernameList = []

        for name in usernames:
            usernameList.append(name.get("username"))

        if username in usernameList:
            return apology("username is taken", "400")

        # Generate hash
        hashValue = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # Vind het hoogste ID
        rows = db.execute("SELECT MAX(id) FROM users")
        MaxID = list(rows[0].values())[0]

        # Generate id
        if not MaxID:
            user_id = 1
        else:
            user_id = MaxID + 1

        # Create a new user in the database
        db.execute("INSERT INTO users (id, username, hash) VALUES (%d, '%s', '%s')" % (user_id, username, hashValue))

        # Remember which user has logged in
        session["user_id"] = user_id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        return
    else:
        return render_template("quiz.html")
    

@socketio.on('message')
def message(data):
    
    print(f"MESSAGE SOCKETIO: {data}")

    send(data)
    emit('some-event', data)

@socketio.on('create_room')
def create_room(data):
    room = data['room']
    display_name = data['display_name']
    room_list[room] = {'party_mode': data['party_mode'], 'players': [display_name]}
    room_guess_scores[room] = {display_name: 0}
    room_point_scores[room] = {display_name: 0}
    room_progress[room] = data['room_progress']

    print(f"User {data['display_name']} has joined room room {data['room']}")
    print(f"Users in room: {room_list[room]['players']}")

    join_room(data['room'])
    print(f"Room scores: {room_guess_scores[room]} and {room_point_scores[room]}")
    socketio.emit('room_created', {'room': room, 'user': display_name, 'guess_scores': room_guess_scores[room], 'point_scores': room_point_scores[room], 'party_mode': room_list[room]['party_mode']}, room=room)


@socketio.on('join')
def join(data):

    room = data['room']
    display_name = data['display_name']

    if room in room_list.keys():
        room_list[room]['players'].append(display_name)
        room_guess_scores[room][display_name] = 0
        room_point_scores[room][display_name] = 0
    
    print(f"User {data['display_name']} has joined room room {data['room']}")
    print(f"Users in room: {room_list[room]}")

    join_room(data['room'])
    socketio.emit('player_joined', {'room': room, 'user': display_name, 'guess_scores': room_guess_scores[room], 'point_scores': room_point_scores[room], 'party_mode': room_list[room]['party_mode']}, room=room)


@socketio.on('leave')
def leave(data):
    leave_room(data['room'])

@socketio.on('get_room_data')
def get_room_users(data):
    room = data['room']
    room_users = room_list[room]
    progress = room_progress[room]
    socketio.emit('room_data', {'room': room, 'users': room_users['players'], 'party_mode': room_list[room]['party_mode'], 'room_progress': progress}, room=request.sid)


@socketio.on('add_pokemon')
def add_pokemon(data):
    dex_id = data['dex_id']
    room = data['room']
    user = data['display_name']
    room_guess_scores[room][user] += 1
    room_progress[room].append(dex_id)

    if room_list[room]['party_mode']:
        room_point_scores[room][user] += 100
        # TODO

    emit('pokemon_added', {'dex_id': dex_id, 'user': user, 'guess_scores': room_guess_scores[room], 'point_scores': room_point_scores[room], 'party_mode': room_list[room]['party_mode']}, room=room)


@socketio.on("sync_timers_request")
def sync_timers_request(data):
    room = data['room']
    emit('timers_sync_request', {'room': room, 'host_name': room_list[room]['players'][0]}, room=room)

@socketio.on("sync_timers")
def sync_timers(data):
    print(data)
    room = data['room']
    hours = data['hours']
    minutes = data['minutes']
    seconds = data['seconds']
    
    emit('timers_synced', {'hours': hours, 'minutes': minutes, 'seconds': seconds}, room=room)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

print(__name__)
if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")
