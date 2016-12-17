$(function(){

	$("#submitbutton").click(function(e){
		$(".loading").removeClass("loading");
	});


	$(".delete-button").click(function(e){
		$(this).parent().parent().toggleClass("remove-artist")
	})

	$(".delete-button").click(function(e){
		$(this).parent().parent().children(".red-x").toggle();
	})

	$(".event-button").click(function(e){
		$(this).addClass("add-artist")
	})


});

