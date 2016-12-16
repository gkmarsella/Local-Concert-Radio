$(function(){

	$("#submitbutton").click(function(e){
		$(".loading").removeClass("loading");
	});


	$(".card").click(function(e){
		$(this).toggleClass("no")
	})


});

