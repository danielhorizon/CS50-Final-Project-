@app.route('/ranking')
def boardRender(boardName):
    
    rows = db.execute("SELECT * FROM boards WHERE board_name = :board_name", board_name = boardName)
    
    if len(rows) == 1:
        boardId = rows[0]["board_id"]
        public = rows[0]["public"]
        memberList = rows[0]["member_user_id"]
        
        if public == "no" and (str(session["user_id"]) not in memberList.split(",")):
            return page_error("Sorry, this board is private.")
        
        posts = db.execute("SELECT posts.*, users.username FROM posts LEFT OUTER JOIN users ON posts.user_id = users.user_id WHERE board_id = :board_id ORDER BY vote_count DESC", board_id = boardId)
        comments = db.execute("SELECT * FROM comments WHERE board_id = :board_id", board_id = boardId)
        
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
        
        return render_template("board.html", posts=posts)
    else:
        return page_error("Sorry, this board does not exist.")