$(document).ready(function(){
	console.log('daef');
	$('button[type=submit]').click(function(){
		console.log('daef');
		console.log($(this).val());
		var z =$(this).val()
		$.ajax({
			url:"http://localhost:8000/complaint_portal/upvote/"+$(this).val(),
			type:"GET",
			success:function(){
				alert("success");
				var x = '#st'+z;
				console.log(x)
				$(x).html("upvoted");
				console.log($('#st2').html());
			},
			error:function(){
				alert("error");
				var x = '#st'+z;
				console.log(x)
				$(x).html("upvoted1");
			}
		});
	});	

});