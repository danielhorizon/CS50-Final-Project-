$('.delete').click(function() {
        
        var result = confirm("Are you sure you want to delete?");
        if (result) {
        //Logic to delete the item
    
        // find the post id
        var postId = $(this).closest("div .post").data("post-id");
        
        console.log(postId);
        
        // for that unique postID, delete it from the SQL table, and remove it from the page 
        // only if the user who is trying to delete is the person who wrote it in the first page 
        
        // get the form data
        var formData = {
            "postId" : postId
        };
        
        $.ajax({
            type : "POST", // define the type of HTTP verb we want to use (POST for our form)
            url : Flask.url_for("delete"), // the url where we want to POST
            data : JSON.stringify(formData), // our data object
            contentType : "application/json",
            dataType: "json", // what type of data do we expect back from the server
            encode: true
        })
        
        .done(function(data){
            console.log(data); 
            
            if (data == "repeatTrash")
            {
                // Turn the trashcan into red or something so the user 
                // can't delete the post twice 
                // "Sorry, you've already deleted this post"
            }
            else {
                // if all is well 
                // remove the post from the page 
            }
        }
        )
        }