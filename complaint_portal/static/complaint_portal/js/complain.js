window.onload = initAll

function initAll(){
	var urlname = window.location.href;
	if(urlname.search("index")!=-1){
		$("ul li").removeClass("active");
		$("#home").addClass("active");
	}
	else if(urlname.search("ranking")!=-1){
		$("ul li").removeClass("active");
		$("#leader_board").addClass("active");
	}
	else if(urlname.search("complainform")!=-1){
		$("ul li").removeClass("active");
		$("#complain").addClass("active");
	}
	else if(urlname.search("userprofile")!=-1){
		$("ul li").removeClass("active");
		$("#myusername").addClass("active");
		$("#localfeeds").addClass("active");
	}
	else if(urlname.search("mycomplains")!=-1){
		$("ul li").removeClass("active");
		$("#myusername").addClass("active");
		$("#complains_my").addClass("active");
	}
	else if(urlname.search("profile_update")!=-1){
		$("ul li").removeClass("active");
		$("#myusername").addClass("active");		
		$("#profile_update").addClass("active");
	}
	else if(urlname.search("logout")!=-1){
		$("ul li").removeClass("active");
		$("#home").addClass("active");
	}
	else if(urlname.search("login")!=-1){
		$("ul li").removeClass("active");
		$("#home").addClass("active");
	}
	else if(urlname.search("faq")!=-1){
		$("ul li").removeClass("active");
		$("#faq").addClass("active");	
	}
	else{
		$("ul li").removeClass("active");
		$("#all_complains").addClass("active");
	}
} 
