$(function(){

	var counter = 0;
	var wildCardCounter = 0;
	var totalTracks = $('ul.hidden').children();
	$.when.apply($, $('ul.hidden').children().map(function(i, el){
		console.log($(el).data());
		return $.ajax({
			type: "POST",
			url: "/get_tracks",
			data: JSON.stringify(($(el).data())),
			contentType: 'application/json',
			dataType: 'json',
			success: function() {
				if(wildCardCounter === 8){
					setTimeout(function(){}, 5000);
					wildCardCounter = 0;
				}

				++counter;
				++wildCardCounter
				$("#loading_player").text((counter / totalTracks.length * 100).toFixed(0) + '% of songs added to playlist')
			}
		})
	})).then(function(data){
		console.log("all Done")
		$("#loading_player").addClass("hidden")
		$(".vertical-slider").addClass("hidden")
		$("#spotify_player").append('<iframe src="' + data[0].url + '" width="100%" height="325" frameborder="0" allowtransparency="true"></iframe>')
	})

	$('.vertical-slider').unslider({
		animation: 'vertical',
		autoplay: true,
		infinite: true,
		nav: false,
		arrows: false
	});


});




















// $(function(){
// 	document.domain = 'spotify.com'
// 	$('.name-ul').children().each(function(i, el){
// 		var dataObj = $(el).data();
// 		dataObj.playlist = $(".pid").data("playlist");
// 		$.ajax({
// 			type: "POST",
// 			url: "/find_tracks",
// 			data: JSON.stringify(dataObj),
// 			contentType: 'application/json',
// 			dataType: 'json',
// 			success: function(data){
// 				var $iframeUl = $('ul.track-list');
// 				$iframeUl.append('<li class="track-row" data-position="' + data['track_row_number'] + '" data-name="' + data['data_name'] + '" data-artists="' + data['data_artists'] + '" data-duration-ms="' +  data['data_duration_ms'] +  '" data-uri="' +  data['data_preview']  +  '" data-web-player-url="' +  data['data_web_player_url'] + '" data-size-640="' + data['data_size_640'] + '" data-size-300="' +  data['data_size_300'] + '" data-size-64="' +  data['data_size_64'] + '" <div class="track-row-number">"' + data['track_row_number'] + '" </div> <div class="track-row-info"> "' + data['track_row_info'] + '" <div class="track-artist"> "' +  data['track_artist']  + '"</div></div><div class="track-row-duration">"' +  data['track_row_duration']  + '"</div></li>');
// 			}
// 		})
// 	})
// // $("iframe#spotify_player").attr('src', function(i, val) { return val; })
// });