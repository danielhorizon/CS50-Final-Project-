//event handler for votes
    $(".vote").click(function() {
        
        // store location of clicked object
        var clicked = $(this);
        
        // search up the DOM tree for the data-post-id
        var postId = clicked.closest("div .post").data("post-id");
        console.log(postId);
        
        if (clicked.hasClass("upvote")) {
            voteType = "upvote";
        }
        else if (clicked.hasClass("downvote")) {
            voteType = "downvote";
        }
        
        // increment count remotely by sending AJAX request
        var voteData = {
            "postId" : postId,
            "voteType" : voteType
        };
        
        $.ajax({
            type : "POST", // HTTP verb
            url : Flask.url_for("newvote"), // url for POST
            data : JSON.stringify(voteData), // data object
            contentType : "application/json", // data sent to server
            dataType: "json", // data expected from server
            encode: true
        })
        .done(function(data) {
            console.log(data);
            // handle repeat votes
            if (data == "repeatUpvote" || data == "repeatDownvote") {
                clicked.addClass("btn-danger").removeClass("btn-primary");
                clicked.children("i").attr("class", "fa fa-exclamation");
                clicked.attr("data-toggle", "tooltip");
                clicked.attr("title", "Sorry, you've already " + voteType + "d!");
                clicked.tooltip("show");
            }
            // otherwise, if all is well
            else {
                // disable this button
                clicked.addClass("btn-success");
                clicked.attr("disabled", "true");
                
                // increment count locally
                count = parseInt(clicked.closest("div .post").find(".count").html(), 10);
                
                if (clicked.hasClass("upvote")) {
                    console.log("yes");
                    // reset downvote
                    clicked.siblings(".btn").removeAttr("disabled");
                    clicked.siblings(".btn").removeAttr("title");
                    clicked.siblings(".btn").removeAttr("data-toggle");
                    clicked.siblings(".btn").tooltip("dispose");
                    clicked.siblings(".btn").attr("class", "btn btn-primary btn-responsive card-link vote downvote");
                    clicked.siblings(".btn").children("i").attr("class", "fa fa-chevron-down");
                    // add one to the count
                    count = count + 1;
                }
                if (clicked.hasClass("downvote")) {
                    // reset upvote
                    clicked.siblings(".btn").removeAttr("disabled");
                    clicked.siblings(".btn").removeAttr("title");
                    clicked.siblings(".btn").removeAttr("data-toggle");
                    clicked.siblings(".btn").tooltip("dispose");
                    clicked.siblings(".btn").attr("class", "btn btn-primary btn-responsive card-link vote upvote");
                    clicked.siblings(".btn").children("i").attr("class", "fa fa-chevron-up");
                    // subtract one from the count
                    count = count - 1;
                }
                
                // update the count
                clicked.closest("div .post").find(".count").html(count);
            }
        })
        .fail(function(data) {
        console.log(data);
        });
    });