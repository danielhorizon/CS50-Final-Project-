import re
import json
import cs50
from cs50 import SQL
from flask import Flask, jsonify, render_template, request, flash, url_for
from flask_jsglue import JSGlue
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
from helpers import *


# configure application
app = Flask(__name__)
JSGlue(app)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response
        
# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)        
        
# configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")
        
@app.route("/")
def index():
    return render_template("board.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # minimise redundancy
        formUsername = request.form.get("username")
        formPassword = request.form.get("password")
        formRepeatPassword = request.form.get("repeatPassword")
        
        # ensure username is entered
        if not formUsername:
            return page_error("must provide username")
            
        # ensure password was submitted
        elif not formPassword:
            return page_error("must provide password")
            
        # ensure password was repeated and that passwords match
        elif not formRepeatPassword or formRepeatPassword != formPassword:
            return page_error("passwords do not match")
            
        # query 'users' table for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=formUsername)
        
        # check if username already exists
        if len(rows) == 1:
            return page_error("username already exists, please try again")

        # add credentials to the 'users' table
        db.execute("INSERT INTO users (username, password) VALUES (:username, :hash)", 
        username=formUsername, hash=pwd_context.encrypt(formPassword))
        
        # login automatically after registration AWESOME
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=formUsername)
        # session for this user only 
        session["user_id"] = rows[0]["user_id"] 
        session["username"] = rows[0]["username"]
        
        # flash a success message
        flash("Thank you for registering, {}. You have been logged in.".format(session["username"]), "info")
        
        # redirect user to home page
        return redirect(url_for("index"))
        
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
        
@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return page_error("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return page_error("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["password"]):
            return page_error("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
        session["username"] = rows[0]["username"]
        
        # flash a success message
        flash("Welcome, {}.".format(session["username"]), "info")

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/receiver", methods=["POST"])
@login_required
def receiver():
    """Adds dynamic data to the database"""
    
    content = request.json
    data = json.loads(content)
    
    db.execute("INSERT INTO comments (postId, comment, userId) VALUES (:postId, : comment, :userId)", 
    postId = data["postId"], comment= data["content"], userId= session["user_id"])

   
@app.route("/newpost", methods=["GET", "POST"])
@login_required
def newpost():
    """Adds dynamic data to the database"""
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        formData = request.get_json()
        
        app.logger.debug(formData["postContent"])
        
        return jsonify(formData)
        
        
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return redirect(url_for("index"))