/*
 var data = {'bob':'foo','paul':'dog'};
 $.ajax({
   url: Flask.url_for("articles")
   type: 'POST',
   contentType:'application/json',
   data: JSON.stringify(data),
   dataType:'json',
   success: function(data){
     //On ajax success do this
     alert(data);
      },
   error: function(xhr, ajaxOptions, thrownError) {
      //On error do this
        if (xhr.status == 200) {

            alert(ajaxOptions);
        }
        else {
            alert(xhr.status);
            alert(thrownError);
        }
    }
 });
*/

$(document).ready(function() {
    
    // a checkbox script (seriously?)
    $("#anonymous").on("click", function () { 
       var $checkbox = $(this).find(':checkbox');
       $checkbox.attr('checked', !$checkbox.attr('checked'));
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
        })
        // using the done promise callback
        .done(function(data) {
            
            console.log(data); 
            
            // do error handling!
        
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
            $('input[id=anonymous]').val('');
            $('.alert-success').remove();
            }, 2500);
        });
        // stop the form from submitting the normal way and refreshing the page
        event.preventDefault();
    });
        
});