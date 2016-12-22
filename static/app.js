$(function(){

	// Displays loading gif when search button is pressed
	$("#submitbutton").click(function(e){
		$(".loading").removeClass("loading");
	});

	$(".create-playlist").click(function(e){
		$(".loading-playlist ").removeClass("loading-playlist ");
	});

	// Adds a class to artist when delete from playlist button is pressed
	$(".delete-button").click(function(e){
		$(this).parent().parent().toggleClass("remove-artist");
	});


	// Places an x over artist image when delete from playlist button is pressed
	$(".delete-button").click(function(e){
		$(this).parent().parent().children(".red-x").toggle();
	});


	// add event utl and artist name to database
	$(".event-button").click(function(e){
		var $clicked = $(this).parent().parent().children(".sort-name");
		var name = $clicked.text().trim();
		var url = $clicked.data('url');
		obj = {name: name, event: url}
		$.ajax({
			type: "POST",
			url: '/event',
			data: JSON.stringify(obj),
			contentType: 'application/json',
			dataType: 'json'
		}).done(function(data){
			var addArtist = data.name
			var addEvent = data.event

			var eventList = $('.fav-event').children()
			var notInList = false
			for(var i=0; i < eventList.length; i++){
				if($(eventList[i]).data('id') === data.id){
					notInList = true
					break
				}
			}
			if(notInList === false){
				$(".fav-event").append('<li data-id="' + data.id + '">' + '<div>' + "Remove from favorites" + '</div>' + '<a href="' + addEvent + '" target="_blank">' + addArtist + "</a></li>" + '<li class="divider"></li>')
			}
		});
	});

	$(".delete-fav").click(function(e){
		$(this).parent('.fav-li').addClass("DELETE")
		
	});


});

