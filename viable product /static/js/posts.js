// the newPost form
    $('#newPost').submit(function(event) {
        
        // get boardName
        var URL = window.location.pathname.split( '/' );
        var boardName = URL[2];
        
        // get the form data
        var formData = {
            "postContent" : $('input[id=postContent], textarea').val(),
            "embedContent" : $('input[id=embedContent]').val(),
            "anonymous" : $('input[id=anonymous]:checked').val(),
            "boardName" : boardName
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
            
            // get boardName
            var URL = window.location.pathname.split( '/' );
            var boardName = URL[2];
            window.location.replace('/board/' + boardName + '/' + URL[3]);
            
        })
        // use the fail promise callback
        .fail(function(data) {
            
        // for errors we don't know about
        console.log(data);
            
        });
        // stop the form from submitting the normal way and refreshing the page
        event.preventDefault();
    });