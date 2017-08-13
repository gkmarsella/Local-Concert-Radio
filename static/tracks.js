$(function(){

	var counter = 0;
	var totalTracks = $('ul.hidden').children();
	$.when.apply($, $('ul.hidden').children().map(function(i, el){
		return $.ajax({
			type: "POST",
			url: "/get_tracks",
			data: JSON.stringify(($(el).data())),
			contentType: 'application/json',
			dataType: 'json',
			success: function() {
				++counter;
				$("#loading_player").text((counter / totalTracks.length * 100).toFixed(0) + '% of songs added to playlist');
			}
		})
	})).then(function(data){
		$("#loading_player").addClass("hidden")
		$(".loading-text").addClass("hidden")
		$("#spotify_player").append('<iframe src="' + data[0].url + '" width="100%" height="100%" frameborder="0" allowtransparency="true"></iframe>');
	})

});