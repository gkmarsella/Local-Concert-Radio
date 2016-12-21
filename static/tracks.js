$(function(){


	$('ul.hidden').children().each(function(i, el){
		$.ajax({
			type: "POST",
			url: "/get_tracks",
			data: JSON.stringify(($(el).data())),
			contentType: 'application/json',
			dataType: 'json'
		})
	})

});