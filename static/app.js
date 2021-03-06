$(function(){

	// Displays loading gif when search button is pressed
	$("#submitbutton").click(function(e){
		$(".loading").removeClass("loading");
	});

	$(".create-playlist").click(function(e){
		$(".loading-playlist ").removeClass("loading-playlist ");
	});

	$(".submitbutton").hover(function(e){
	
	})




	$("#state").change(function(e){
		var stateCode = $(this).val();
		$(this).parent().parent().children('.city-div').children().addClass(stateCode);
		var selected = $(this).parent().parent().children('.city-div').children();

		if(selected.children('.' + stateCode) !== stateCode){
			selected.children().addClass('hidden');
		}

		if(selected.children('.' + stateCode)){
			selected.children('.' + stateCode).removeClass('hidden')
		} 
	});

	$("#submitbutton").click(function(e){
		$("#loading-icon").removeClass("hidden");
	})


	// add event url and artist name to database
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


	$(".confirm").hover(function(){
	    $(this).css("background-color", "#133e6e");
	    }, function(){
	    $(this).css("background-color", "#335983");
	});

		$("#myTextInput").keyup(function() {
	    var text = $(this).val();
	    text = processText(text);
	    $("#secondTextField").val(text);
	});
	
});

