$(function(){



	$.when.apply($, $('ul.hidden').children().map(function(i, el){
		var dataObj = $(el).data();
		dataObj.playlist = $(".pid").data("playlist");
		return $.ajax({
			type: "POST",
			url: "/get_tracks",
			data: JSON.stringify(dataObj),
			contentType: 'application/json',
			dataType: 'json'
		})
	})).then(function(data){
		console.log("URL", data[0].url)
		$("#spotify_player").append('<iframe src="' + data[0].url + '" width="100%" height="325" frameborder="0" allowtransparency="true"></iframe>')
	})


});