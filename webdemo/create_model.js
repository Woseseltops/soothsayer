$(document).ready(function() {

    $('img').hide();

	$('.button').click(function()
       {
		user = $('.user').val().replace('@','');

		$.get('log_file',{user: user}, function(data)
		{
			$('.logtext').html(data);
		});

		$.get('create_model_procedure',{user: user});
        
        $('img').show();

    	window.setInterval(update_log,2000);	

       });

	function update_log()
	{
		user = $('.user').val().replace('@','');
		$.get('log_file',{user: user}, function(data)
		{
			$('.logtext').html(data);
            
            if(data.indexOf("testen") != -1)
            {
                $('img').hide();
            }

		});

	}

});
