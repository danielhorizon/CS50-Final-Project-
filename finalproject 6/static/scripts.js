$(document).ready(function() {
    
    //var socket = null;
    
    // When the connection is open, send some data to the server
    //socket = new WebSocket("ws://" + document.domain + ":8080/websocket/");

    //socket.onopen = function() {
    //    socket.send("Joined");
    //};

    //socket.onmessage = function(message) {
    //    var txt = message.data;
    //    $(".container").append("<p>" + txt + "</p>");
    //};

    //function submit() {
    //var text = $("input#message").val();
    //socket.send(text);
    //$("input#message").val('');
    //};
    
    
    // enable Bootstrap tool tips
    $('[data-toggle="tooltip"]').tooltip();
    
    // enable Bootstrap comment collapse
    $(".show-comments").click(function() {
        $(this).closest("div .post").find(".comment-block").collapse("toggle");
    });
    
    // the newPost form
    $('#newPost').submit(function(event) {
        
        // get the form data
        var formData = {
            "postContent" : $('input[id=postContent], textarea').val(),
            "embedContent" : $('input[id=embedContent]').val(),
            "anonymous" : $('input[id=anonymous]:checked').val()
        };
        
        console.log(formData);
        
        // process the form
        $.ajax({
            type : "POST", // define the type of HTTP verb we want to use (POST for our form)
            url : Flask.url_for("newpost"), // the url where we want to POST
            data : JSON.stringify(formData), // our data object
            contentType : "application/json",
            dataType: "json", // what type of data do we expect back from the server
            encode: true
        })
        // using the done promise callback
        .done(function(data) {
            
            console.log(data); 
            
            // if validation errors were sent back
            if (data["errors"]) {
                if (data["errors"].indexOf("emptyPostContent") > -1) 
                {
                    $('#postContent').addClass('form-control-warning');
                    $('.postContent').append('<p>' + 'Your post content cannot be empty!' + '</p>');
                }
                if (data["errors"].indexOf("embedBroken") > -1) 
                {
                    $('#embedContent').addClass('form-control-warning');
                    $('.embedContent').append('<div class="form-control-feedback">' + 'Your embed URL is broken!' + '</div>');
                }
            }
            else {
                
                // show the success message, removing previous ones if they exist
                var successMessage = $('.alert-success');
                if (successMessage) {
                    successMessage.remove();
                    $('#newPost').append('<div class="alert alert-success">' + 'Post submitted!' + '</div>');
                    
                }
                // close the form after a time delay
                setTimeout(function(){ $('#postForm').collapse("hide") }, 2000);
                
                // erase form contents for next use after a time delay
                setTimeout(function(){
                $('input[id=postContent], textarea').val('');
                $('input[id=embedContent]').val('');
                $('input[id=anonymous]').val('no');
                $('.alert-success').remove();
                }, 2500);
                }
        })
        // use the fail promise callback
        .fail(function(data) {
            
        // for errors we don't know about
        console.log(data);
            
        });
        // stop the form from submitting the normal way and refreshing the page
        event.preventDefault();
    });
    
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

    // the newComment form
    $('.newcomment').submit(function(event) {
        
        // find the post id
        var postId = $(this).closest("div .post").data("post-id");
        
        console.log(postId);
        
        var commentContent = $(this).find("#commentContent").val();
        var commentId = '#' + $(this).attr('id');
        console.log(commentId);
        
        
        console.log(commentContent);
        
        // get the form data
        var formData = {
            "commentContent" : commentContent,
            "postId" : postId
        };
        
        console.log(formData);
        
        // process the form
        $.ajax({
            type : "POST", // define the type of HTTP verb we want to use (POST for our form)
            url : Flask.url_for("newcomment"), // the url where we want to POST
            data : JSON.stringify(formData), // our data object
            contentType : "application/json",
            dataType: "json", // what type of data do we expect back from the server
            encode: true
        })
        // using the done promise callback
        .done(function(data) {
            console.log(data); 
            var successMessage = $('.alert-success');
            var errorMessage = $('.alert-danger');
            if (data == "emptyCommentContent") {
                if (errorMessage) {
                    errorMessage.remove();
                }
                $(commentId).append('<div class="alert alert-danger">' + 'Your comment cannot be empty. Please try again.' + '</div>');
            }
            else {
                // show the success message, removing previous ones if they exist
                if (successMessage) {
                    errorMessage.remove();
                    successMessage.remove();
                    $(commentId).append('<div class="alert alert-success">' + 'Comment submitted!' + '</div>');
                }
                // erase form contents for next use after a time delay
                setTimeout(function(){
                $('input[id=commentContent], textarea').val('');
                $('.alert-success').remove();
                }, 2500);
            }
        })
        // use the fail promise callback
        .fail(function(data) {
            console.log(data);
        });
        // stop the form from submitting the normal way and refreshing the page
        event.preventDefault();
    });
    
    // autorefresh page 
    // setInterval(function() {
        // $("#refresh").load(Flask.url_for("index") + ' #refresh');
    // }, 5000);
});
    
    
