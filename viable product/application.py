import re
import json
import cs50
from cs50 import SQL
from flask import Flask, jsonify, render_template, request, flash, url_for
from flask_jsglue import JSGlue
from flask_session import Session

#from flask_sockets import Sockets
from tornado.wsgi import WSGIContainer
from tornado.web import Application, FallbackHandler
from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop

from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
from helpers import *

# establish web socket
#sio = socketio.Server()

# configure application
app = Flask(__name__)
JSGlue(app)
#sockets = Sockets(app)

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


#class WebSocket(WebSocketHandler):
#    def open(self):
#        print("Socket opened.")
#
#    def on_message(self, message):
##        self.write_message("Received: " + message)
#        print("Received message: " + message)
#
#def on_close(self):
#    print("Socket closed.")

@app.route("/")
def index():
    
    return render_template("index.html")
    
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
        
        # error-handling:
        errors = {"errors" : [] }
        
        # formData contains postContent, embedContent, anonymous
        formData = request.get_json()
        
        # get boardId
        rows = db.execute("SELECT * FROM boards WHERE board_name = :board_name", board_name = formData["boardName"])
        if len(rows) == 1:
            boardId = rows[0]["board_id"]
            formData.update({"boardId" : boardId})
        else:    
            errors["errors"].append("boardNameNotExist")    
        
        # add the userId from session
        formData.update({"userId": session["user_id"]})
        
        # parse the embedContent url to usable HTML
        embedHTML = ""
        # attempt embedContentHelper only if valid URL
        if ("http://" in formData["embedContent"]) or ("https://" in formData["embedContent"]):
            embedHTML = embedContentHelper(formData["embedContent"])
        
        # ERROR HANDLING
        # if postContent is empty
        if formData["postContent"] == "":
            errors["errors"].append("emptyPostContent")
        ## if embedContent is broken    
        if embedHTML == "embedBroken":
            errors["errors"].append("embedBroken")
        # return errors if they exist
        if errors["errors"]:
            return jsonify(errors)
        
        # add the data to the 'posts' table in the database
        rows = db.execute("INSERT INTO posts (user_id, post_content, embed_content, anonymous, board_id) VALUES (:user_id, :post_content, :embed_content, :anonymous, :board_id)",
        user_id=formData["userId"], post_content=formData["postContent"], embed_content=embedHTML, anonymous=formData["anonymous"], board_id=formData["boardId"])
        
        # update the post count in the 'boards' table in the database
        rows = db.execute("SELECT post_count FROM boards WHERE board_id = :board_id", board_id = formData["boardId"])
        postCount = rows[0]["post_count"] + 1
        app.logger.debug(postCount)
        rows = db.execute("UPDATE boards SET post_count = :post_count WHERE board_id = :board_id", post_count = postCount, board_id = formData["boardId"])


        return jsonify(formData)
        
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return redirect(url_for("index"))

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():  
     
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # success
        
        rows = db.execute("SELECT user_id FROM posts WHERE user_id = :user_id AND post_id = :post_id",
        user_id=["userId"], post_id=["postId"])
        ID = rows[0]["user_id"]
        
        if ID == session["user_id"]: 
            db.execute("DELETE FROM posts WHERE user_id = :user_id", user_id = ID) 
        
        return jsonify("comment deleted")
        
    else:
        return redirect(url_for("index"))


@app.route("/newvote", methods=["GET", "POST"])
@login_required
def newvote():        
        
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # check if user logged in
        if not session["user_id"]:
            return jsonify("login to vote")
            
        # voteData contains voteType and postId only
        voteData = request.get_json()
        
        # add the userId from session
        voteData.update({"userId": session["user_id"]})
        
        if voteData["voteType"] == "upvote":
            
            # check for existing vote
            rows = db.execute("SELECT * FROM votes WHERE user_id = :user_id AND post_id = :post_id",
            user_id=voteData["userId"], post_id=voteData["postId"])
            
            # if vote exists
            if len(rows) == 1:
                # prevent repeat upvote
                if rows[0]["vote_type"] == 1:
                    return jsonify("repeatUpvote")
                # update downvote to upvote
                elif rows[0]["vote_type"] == -1:
                    # update in votes table
                    rows = db.execute("UPDATE votes SET vote_type = :vote_type WHERE post_id = :post_id AND user_id = :user_id",
                    vote_type="1", post_id=voteData["postId"], user_id=voteData["userId"])
                    # update count in posts table
                    rows = db.execute("SELECT * FROM posts WHERE post_id = :post_id", post_id=voteData["postId"])
                    count = rows[0]["vote_count"] + 1
                    rows = db.execute("UPDATE posts SET vote_count = :vote_count WHERE post_id = :post_id",
                    vote_count=count, post_id=voteData["postId"])
            # if vote does not exist        
            elif len(rows) == 0:
                # add row to 'votes' table with user_id, post_id, board_id, vote_type = 1
                rows = db.execute("INSERT INTO votes (user_id, post_id, board_id, vote_type) VALUES (:user_id, :post_id, :board_id, :vote_type)",
                user_id=voteData["userId"], post_id=voteData["postId"], board_id="0", vote_type="1")
                # update count in posts table
                rows = db.execute("SELECT * FROM posts WHERE post_id = :post_id", post_id=voteData["postId"])
                count = rows[0]["vote_count"] + 1
                rows = db.execute("UPDATE posts SET vote_count = :vote_count WHERE post_id = :post_id",
                vote_count=count, post_id=voteData["postId"])
            
            return jsonify("upvoted")

        elif voteData["voteType"] == "downvote":
            
            # check for existing vote
            rows = db.execute("SELECT * FROM votes WHERE user_id = :user_id AND post_id = :post_id",
            user_id=voteData["userId"], post_id=voteData["postId"])
            
            # if vote exists
            if len(rows) == 1:
                # prevent repeat downvote
                if rows[0]["vote_type"] == -1:
                    return jsonify("repeatDownvote")
                # update downvote to upvote
                elif rows[0]["vote_type"] == 1:
                    # update in votes table
                    rows = db.execute("UPDATE votes SET vote_type = :vote_type WHERE post_id = :post_id AND user_id = :user_id",
                    vote_type="-1", post_id=voteData["postId"], user_id=voteData["userId"])
                    # update count in posts table
                    rows = db.execute("SELECT * FROM posts WHERE post_id = :post_id", post_id=voteData["postId"])
                    count = rows[0]["vote_count"] - 1
                    rows = db.execute("UPDATE posts SET vote_count = :vote_count WHERE post_id = :post_id",
                    vote_count=count, post_id=voteData["postId"])
            # if vote does not exist        
            elif len(rows) == 0:
                # add row to 'votes' table with user_id, post_id, board_id, vote_type = 1
                rows = db.execute("INSERT INTO votes (user_id, post_id, board_id, vote_type) VALUES (:user_id, :post_id, :board_id, :vote_type)",
                user_id=voteData["userId"], post_id=voteData["postId"], board_id="0", vote_type="-1")
                # update count in posts table
                rows = db.execute("SELECT * FROM posts WHERE post_id = :post_id", post_id=voteData["postId"])
                count = rows[0]["vote_count"] - 1
                rows = db.execute("UPDATE posts SET vote_count = :vote_count WHERE post_id = :post_id",
                vote_count=count, post_id=voteData["postId"])
                
            return jsonify("downvoted")    
        
        # if voteData contains neither upvote nor downvote    
        else:
            return jsonify("unexpected error")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return redirect(url_for("index"))
   

@app.route("/newcomment", methods=["GET", "POST"])
@login_required
def newcomment():
    """Adds dynamic data to the database"""
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # error-handling:
        errors = {"errors" : [] }
        
        # formData contains commentContent, postId
        formData = request.get_json()
        
        app.logger.debug(formData)
        
        # add the userId from session
        formData.update({"userId": session["user_id"]})
        
        # ERROR HANDLING
        # if postContent is empty
        if formData["commentContent"] == "":
            return jsonify("emptyCommentContent")
        
        # add row to 'comments' table with user_id, post_id, comment_content
        rows = db.execute("INSERT INTO comments (user_id, post_id, comment_content) VALUES (:user_id, :post_id, :comment_content)",
        user_id=formData["userId"], post_id=formData["postId"], comment_content=formData["commentContent"])
                
        # update count in posts table
        rows = db.execute("SELECT * FROM posts WHERE post_id = :post_id", post_id=formData["postId"])
        count = rows[0]["comment_count"] + 1
        rows = db.execute("UPDATE posts SET comment_count = :comment_count WHERE post_id = :post_id",
        comment_count=count, post_id=formData["postId"])
        
        # success
        return jsonify("comment added")
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return redirect(url_for("index"))
        

@app.route('/board')
@login_required
def boardList():
    """Whereas /board/<boardname> renders a specific board, this function renders a list of a user's boards."""
    
    userId = session["user_id"]
    
    # this SQL query checks for membership in a comma-separated list of member_user_id column in table 'boards'
    # it also runs a parallel query on 'users' to find the creator_user_id username
    rows = db.execute("SELECT boards.*, users.username FROM boards LEFT OUTER JOIN users ON boards.creator_user_id = users.user_id WHERE (',' + RTRIM(member_user_id) + ',') LIKE '%,' + :member_user_id + ',%'",
    member_user_id = userId)
    
    # this SQL query checks if the user has created any boards
    # it also runs a parallel query on 'users' to find the creator_user_id username
    rows2 = db.execute("SELECT boards.*, users.username FROM boards LEFT OUTER JOIN users ON boards.creator_user_id = users.user_id WHERE creator_user_id = :creator_user_id", creator_user_id = userId)
    
    # combine both results
    rows3 = rows + [x for x in rows2 if x not in rows]
    
    # this function converts the timestamp of the results of the SQL query
    for row in rows3:
        dt = datetime.datetime.strptime(row["timestamp"], '%Y-%m-%d %H:%M:%S')
        row["timestamp"] = convertToHumanReadable(dt)

    return render_template("boardlist.html", rows=rows)

@app.route('/posts')
@login_required
def postList():
    """This function renders a list of a user's posts."""
    
    userId = session["user_id"]
    
    posts = db.execute("SELECT posts.*, users.username FROM posts LEFT OUTER JOIN users ON posts.user_id = users.user_id WHERE posts.user_id = :user_id ORDER BY timestamp DESC", user_id = userId)
    
    for post in posts:
        dt = datetime.datetime.strptime(post["timestamp"], '%Y-%m-%d %H:%M:%S')
        post["timestamp"] = convertToHumanReadable(dt)
        comments = db.execute("SELECT comments.*, users.username FROM comments LEFT OUTER JOIN users ON comments.user_id = users.user_id WHERE post_id = :post_id ORDER BY timestamp DESC", post_id = post["post_id"])
        for comment in comments:
            dt = datetime.datetime.strptime(comment["timestamp"], '%Y-%m-%d %H:%M:%S')
            comment["timestamp"] = convertToHumanReadable(dt)
        post.update({"comment_list" : comments})
        
    
    app.logger.debug(posts[0])    
    
    
    return render_template("postlist.html", posts=posts)
    
@app.route('/board/<path:boardName>/')    
@app.route('/board/<path:boardName>/<path:sort>')    
def boardRender(boardName, sort="recent"):
    
    if sort != "recent" and sort != "popular":
        return page_error("This URL does not exist.")
    
    check = ""   
    if sort == "recent":
        order = "timestamp DESC"
    elif sort == "popular":
        check = 'checked'
        order = "vote_count DESC"
        
    rows = db.execute("SELECT * FROM boards WHERE board_name = :board_name", board_name = boardName)
    
    if len(rows) == 1:
        boardId = rows[0]["board_id"]
        public = rows[0]["public"]
        memberList = rows[0]["member_user_id"]
        
        if public == "no" and (str(session["user_id"]) not in memberList.split(",")):
            return page_error("Sorry, this board is private.")
        
        posts = db.execute("SELECT posts.*, users.username FROM posts LEFT OUTER JOIN users ON posts.user_id = users.user_id WHERE board_id = :board_id ORDER BY {}".format(order), board_id = boardId)
        comments = db.execute("SELECT comments.*, users.username FROM comments LEFT OUTER JOIN users ON comments.user_id = users.user_id WHERE board_id = :board_id ORDER BY timestamp DESC", board_id = boardId)
        
        for post in posts:
            dt = datetime.datetime.strptime(post["timestamp"], '%Y-%m-%d %H:%M:%S')
            post["timestamp"] = convertToHumanReadable(dt)
        
        for comment in comments:
            dt = datetime.datetime.strptime(comment["timestamp"], '%Y-%m-%d %H:%M:%S')
            comment["timestamp"] = convertToHumanReadable(dt)
        
        for post in posts:
            commentList = []
            for comment in comments:
                if post["post_id"] == comment["post_id"]:
                    commentList.append(comment.copy())
            post.update({"comment_list" : commentList})
           
        # if the votes on the post <-5, then delete it  
        for post in posts: 
            if post["vote_count"] <= -5: 
                # remove post from posts 
                posts.remove(post)
                # remove from SQL table 
                db.execute("DELETE FROM posts WHERE post_id = :post_id", post_id = post["post_id"])
        
        return render_template("board.html", posts=posts, boardName=boardName, check=check)
    else:
        return page_error("Sorry, this board does not exist.")
        
@app.route("/newboard", methods=["GET", "POST"])
@login_required
def newboard():        
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # check if user logged in
        if not session["user_id"]:
            return jsonify("nologin")
            
        formData = request.get_json()  
        
        # minimise redundancy
        boardTitle = formData["boardTitle"]
        boardName = formData["boardName"]
        public = formData["public"]
        userId = session["user_id"]
        username = session["username"]
        memberList = formData["memberList"]
        
        app.logger.debug(memberList)
        # memberList is a comma separated string
        
        # append user_name to list if not in it
        if userId not in memberList:
            memberList.append(userId)
        stringMemberList = ",".join(map(str, memberList))
        
        # check if boardname funky
        if boardName.isalnum() == False:
            return jsonify("boardNameIncorrect")
        
        # check if boardtitle empty
        if boardTitle == "":
            return jsonify("boardTitleEmpty")
        
        # check if boardname unique
        rows = db.execute("SELECT * FROM boards WHERE board_name = :board_name", board_name = boardName)
        if len(rows) != 1:
            # add data to 'boards' table
            rows = db.execute("INSERT INTO boards (board_title, board_name, public, creator_user_id, member_user_id) VALUES (:board_title, :board_name, :public, :creator_user_id, :member_user_id)",
            board_title = boardTitle, board_name = boardName, public = public, creator_user_id = userId, member_user_id = stringMemberList)
            return jsonify("success") 
        else:
            return jsonify("boardNameExists")
        
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("newboard.html")   
    
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search for the usernames for typeahead"""
   
    if not request.args.get("q"):
        raise RuntimeError("missing query")
    
    parloc = request.args.get("q") + "%"
    users = db.execute('SELECT username, user_id FROM users WHERE username LIKE :q ', q=parloc)
       
    return jsonify(users)
    
@app.route("/boardsearch", methods=["GET", "POST"])
@login_required
def boardsearch():
    """Search for the usernames for typeahead"""
   
    if not request.args.get("q"):
        raise RuntimeError("missing query")
    
    parloc = request.args.get("q") + "%"
    boards = db.execute('SELECT board_title, board_name FROM boards WHERE board_name LIKE :q OR board_title LIKE :q', q=parloc)
       
    return jsonify(boards)



#@app.route("/posts", methods=["GET", "POST"])
#@login_required
#def posts():
#    data = request.get_json()
#    rows = db.execute("SELECT * FROM boards WHERE board_name = :board_name", board_name = data["boardName"])
#    counter = 10 * data["counter"]
#    return jsonify(rows[(counter - 1):counter]))
    
# DANGER DANGER DANGER        
@app.route('/remoteshutdown', methods=['GET'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
@app.route('/sessionquery', methods=['GET'])
@login_required
def sessionquery():
    sessionList = { "userId" : session["user_id"], "username": session["username"] }
    return jsonify(sessionList)    
    
    