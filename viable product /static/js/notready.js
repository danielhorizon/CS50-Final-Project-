function search(query, syncResults, asyncResults)
{
    // get places matching query (asynchronously)
    var parameters = {
        q: query
    };
    $.getJSON(Flask.url_for("search"), parameters)
    .done(function(data, textStatus, jqXHR) {
     
        // call typeahead's callback with search results (i.e., places)
        asyncResults(data);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
 
        // log error to browser's console
        console.log(errorThrown.toString());
 
        // call typeahead's callback with no results
        asyncResults([]);
    });
}

function boardsearch(query, syncResults, asyncResults)
{
    // get places matching query (asynchronously)
    var parameters = {
        q: query
    };
    $.getJSON(Flask.url_for("boardsearch"), parameters)
    .done(function(data, textStatus, jqXHR) {
     
        // call typeahead's callback with search results (i.e., places)
        asyncResults(data);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
 
        // log error to browser's console
        console.log(errorThrown.toString());
 
        // call typeahead's callback with no results
        asyncResults([]);
    });
}


//////////

function checkAvailability() {
    $("#loaderIcon").show();
    jQuery.ajax({
    url: "check_availability.php",
    data:'username='+$("#username").val(),
    type: "POST",
    success:function(data){
    $("#user-availability-status").html(data);
    $("#loaderIcon").hide();
    },
    error:function (){}
    });
}

///////

function sessionQuery()
{
    $.getJSON(Flask.url_for("sessionquery"))
    .done(function(data) {
    return data; 
    })
    .fail(function(data) {
        console.log(data);
    });
}