import re
import json
import cs50
from cs50 import SQL
from flask import Flask, jsonify, render_template, request, url_for
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
        
        # redirect user to home page
        return redirect(url_for("index"))
        
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")