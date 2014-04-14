$(document).ready(function(){
	console.log('daef');
	$('button[type=submit]').click(function(){
		console.log('daef');
		console.log($(this).val());
		var z =$(this).val()
		$.ajax({
			url:"http://localhost:8000/complaint_portal/upvote/"+$(this).val(),
			type:"GET",
			success:function(d){

				//alert("dsd");
				console.log(d["upvotes"]);
				var x = '#st'+z;
				console.log(x)
				$(x).html(d["upvotes"]);
				console.log($(x).html());
			},
			error:function(d){
				//alert(d);
				console.log(d);
				var x = '#st'+z;
				console.log(x)
				$(x).html("upvoted1");
			}
		});
	});	

});