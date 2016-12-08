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