$(function(){



	$.when.apply($, $('ul.hidden').children().map(function(i, el){
		return $.ajax({
			type: "POST",
			url: "/get_tracks",
			data: JSON.stringify(($(el).data())),
			contentType: 'application/json',
			dataType: 'json'
		})
	})).then(function(data){
		console.log("all Done")


		$("#spotify_player").append('<iframe src="' + data[0].url + '" width="100%" height="325" frameborder="0" allowtransparency="true"></iframe>')
	})


});