$.getScript('/static/js/notready.js')
	.done(function() {
	})
	.fail(function() {
    });

$(document).ready(function() {
        

    // jQuery unveil
    //$("img").unveil(200);
    
    // enable Bootstrap tool tips
    $('[data-toggle="tooltip"]').tooltip();
    
    $.getScript('/static/js/posts.js')
	.done(function() {
	})
	.fail(function() {
    });
    
    $.getScript('/static/js/votes.js')
	.done(function() {
	})
	.fail(function() {
    });
    
    $.getScript('/static/js/comments.js')
	.done(function() {
	})
	.fail(function() {
    });
    
    $.getScript('/static/js/boards.js')
	.done(function() {
	})
	.fail(function() {
    });
    
    $.getScript('/static/js/scroll.js')
	.done(function() {
	})
	.fail(function() {
    });
    
    $.getScript('/static/js/flipswitch.js')
	.done(function() {
	})
	.fail(function() {
    });
    
    
 
// end document ready    
});


