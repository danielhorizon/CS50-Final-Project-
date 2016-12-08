// enable Bootstrap newBoard collapse
    $(".private").click(function() {
        $(".addUsers").collapse("show");
    });
    $(".public").click(function() {
        $(".addUsers").collapse("hide");
    });
    

// the newBoard form
    $('#newBoard').submit(function(event) {
        
        // get the form data
        var formData = {
            "boardName" : $('input[name=boardName]').val(),
            "boardTitle" : $('input[name=boardTitle]').val(),
            "public" : $('input[id=public]:checked').val(),
            "memberList" : memberList
        };
        
        console.log(formData);
        
        // process the form
        $.ajax({
            type : "POST", // define the type of HTTP verb we want to use (POST for our form)
            url : Flask.url_for("newboard"), // the url where we want to POST
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
            if (data == "boardNameExists") {
                if (errorMessage) {
                    errorMessage.remove();
                }
                $("#newBoard").append('<div class="alert alert-danger">' + 'Your chosen board name already exists. Please choose another.' + '</div>');
            }
            else if (data == "boardNameIncorrect") {
                if (errorMessage) {
                    errorMessage.remove();
                }
                $("#newBoard").append('<div class="alert alert-danger">' + 'Your board name is not alphanumeric. Type in atleast one character/number, with no spaces or symbols.' + '</div>');
            }
            else if (data == "boardTitleEmpty") {
                if (errorMessage) {
                    errorMessage.remove();
                }
                $("#newBoard").append('<div class="alert alert-danger">' + 'You cannot leave the board title blank.' + '</div>');
            }
            else {
                // show the success message, removing previous ones if they exist
                if (successMessage) {
                    errorMessage.remove();
                    successMessage.remove();
                    $("#newBoard").append('<div class="alert alert-success">' + 'Board created. Find it at /boards/' + formData["boardName"] + '</div>');
                }
                // erase form contents for next use after a time delay
                setTimeout(function(){
                $('input[id=commentContent], textarea').val('');
                $('input[name=boardName]').val('');
                $('input[name=boardTitle]').val('');
                $('input[id=public]:checked').val('yes');
                $("#memberList").val('');
                memberList = [];
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
    
    
// scripts for the addUserTypeahead
    $("#q").typeahead({
        highlight: false,
        minLength: 1
    },
    {
        display: function(suggestion) { return null; },
        limit: 10,
        source: search,
        templates: {
            suggestion: Handlebars.compile(
                "<div>" +
                "{{username}}"+
                "</div>"
            )
        }
    });
    var memberList = [];
    // create user tags when typeahead selected
    $("#q").on("typeahead:selected", function(eventObject, suggestion, name) {
        // create variables
        var username = suggestion["username"];
        var user_id = suggestion["user_id"];
        // if username not in memberList and not session username
        if ($.inArray(user_id, memberList) == -1) {
            // append it to list
            $("#addedUsernames").append("<span data-user-id='" + suggestion["user_id"] + "'" + " class='tag tag-success custom-user-tag'>" + username + "</span>");
            // add to memberList
            memberList.push(user_id);
        }
        // create stringMemberList
        var stringMemberList = memberList.join(",");
        $("#memberList").val(stringMemberList);
    });
    // remove user tags when clicked
    $(document).on('click','.custom-user-tag',function(){
        // get user-id from tag
        var user_id = $(this).data("user-id");
        var index = memberList.indexOf(user_id);
        if (index > -1) {
            memberList.splice(index, 1);
        }
        var stringMemberList = memberList.join(",");
        $("#memberList").val(stringMemberList);
        $(this).remove();
    });
    // scripts for the FindBoard
    $("#f").typeahead({
        highlight: false,
        minLength: 1
    },
    {
        display: function(suggestion) { return null; },
        limit: 10,
        source: boardsearch,
        templates: {
            suggestion: Handlebars.compile(
                "<div>" +
                "{{board_title}}" + ' (' + "{{board_name}}" + ')' +
                "</div>"
            )
        }
    });
    
    $("#f").on("typeahead:selected", function(eventObject, suggestion, name) {
        
        window.location.replace('/board/' + suggestion.board_name);
    });

    

    
// flipswitch for popularity
$(function() {
    $('#flipswitch').bootstrapToggle({
      on: 'Enabled',
      off: 'Disabled'
    });
})

// enable Bootstrap add users collapse for board list
    $(".show-add-users").click(function() {
        $(this).closest("div .board").find(".add-users").collapse("toggle");
    });