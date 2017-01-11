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
			var addArtist = data.name;
			var addEvent = data.event;

			var eventList = $('.fav-event').children()
			var notInList = false
			for(var i=0; i < eventList.length; i++){
				if($(eventList[i]).data('id') === data.id){
					notInList = true;
					break;
				}
			}
			if(notInList === false){
				$(".fav-event").append('<li class="fav-li" data-id="' + data.id + '">' + '<img src="static/images/x-icon.png" class="delete-fav">' + '<a href="' + addEvent + '" target="_blank" id="fav-a">' + addArtist + "</a></li>" + '<li class="divider"></li>')
			}
		});
	});


	// DELETE EVENTS
	$(".fav-event").click(function(e){
		if(e.target.className === "delete-fav"){
			var listId = $(e.target).parent().data('id');
			$.ajax({
				type: "DELETE",
				url: '/event/' + listId,
				success: function(msg){
					$(e.target).parent().siblings(".divider").eq(0).remove();		
					$(e.target).parent('.fav-li').remove();
				}
			});
		};
	});


	$(document).ready(function(){
    	$('#results-table').DataTable();		
    });

	    $('input[name="daterange"]').daterangepicker();


});

