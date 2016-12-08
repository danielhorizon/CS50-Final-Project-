$('input[id=toggle]:checked').click(function() {
    $('#refresh').load(Flask.url_for("ranking") + ' #refresh');
});

$('#recent').click(function() {
    // get boardName
    var URL = window.location.pathname.split( '/' );
    var boardName = URL[2];
    
    $('#refresh').load(Flask.url_for(boardName) + ' #refresh');
});



<script>
  $(function() {
    $('#toggle').bootstrapToggle({
      on: 'Recent',
      off: 'Popular'
    });
  })
</script>

$('input[id=toggle]:checked')

$('#toggle').change(function() {
    
    if $(this).prop('checked') == true {
        console.log('true');
    }
}

   
   
   
    $('[data-toggle="popover"]').popover();  // initialize popover
    
    $('input[id=toggle]:checked').click(function() {
        
        console.log('logged');
    
        
        $('#refresh').load(Flask.url_for("ranking") + ' #refresh');
    
    });