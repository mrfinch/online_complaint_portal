'''implementing views corresponding to given url
Authors:Saurabh,Amit,Shikha,Nidhi,Noopur
'''
from django.shortcuts import render
from complaint_portal.models import *
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
import random,string
from datetime import datetime,timedelta 
from django.db.models import Q
import django.core.exceptions
import json
# Create your views here.

def index(request):
	'''Home page'''
	current_complains = Complain.objects.order_by('complain_date')[:3]
	total_comp = Complain.objects.count()
	solved_comp = Complain.objects.filter(Q(govt_complain_status=2) | Q(govt_complain_status=3)).count()
	return render(request,"complaint_portal/index.html",{"current_complains":current_complains,"total_comp":total_comp,
		"solved_comp":solved_comp})

def faq(request):
	'''faq page'''
	return render(request,"complaint_portal/faq.html",{})
	
def register(request):
	'''register page'''
	places = LocalPlaces.objects.all()
	if request.method == "POST":
		form = UserInfoForm(request.POST)
		if not request.POST.get("phone","").isdigit():
			return render(request,"complaint_portal/register.html",{"msg":"Phone no. should have only numeric digits","places":places})
		if form.is_valid():
			username = form.cleaned_data["username"]
			firstname = form.cleaned_data["first_name"]
			lastname = form.cleaned_data["last_name"]
			email = form.cleaned_data["email"]
			password = form.cleaned_data["password"] #confirm_password check on frontend
			address	= request.POST.get("address","")
			phone = request.POST.get("phone","")
			locality = request.POST.get("locality","")
			user = User.objects.create_user(username=username,first_name=firstname,last_name=lastname,email=email,password=password)
			#user.is_active = False
			user.is_active = True
			user.save()
			userinfo = UserInfos.objects.create(id=user.id,user_id=user.id,address=address,phone=phone,locality=locality)
			#url = "http://localhost:8000/complaint_portal/" + "activate/" + str(user.id)
			#send_mail("Activate your account",url,"saurabh.finch@gmail.com",[user.email])
			return render(request,"complaint_portal/register.html",{"places":places,"msg":"Account Registered. Activate it by clicking link sent to your registered email"})
		else:
			return render(request,"complaint_portal/register.html",{"msg":form.errors,"places":places})
	else:
		return render(request,"complaint_portal/register.html",{"places":places})			

def login(request):
	'''login of all users,middlemen,govt employee and redirecting them acc' to their permissions'''
	if request.method == "POST":
		username = request.POST.get("username","")
		password = request.POST.get("password","")
		user = auth.authenticate(username=username,password=password)
		if user is not None and user.is_staff:
			auth.login(request,user)
			return HttpResponseRedirect(reverse('complaint_portal:middlemen'))	
		elif user is not None and user.is_superuser:
			auth.login(request,user)
			return HttpResponseRedirect(reverse('complaint_portal:govtadmin'))
		elif user is not None and user.is_active:
			auth.login(request,user)
			return HttpResponseRedirect(reverse('complaint_portal:mycomplains'))
		else:
			return render(request,"complaint_portal/index.html",{"msg":"Username and Password combination incorrect"})
	
def activate(request,u_id):
	'''activating account thro' email'''
	u = User.objects.get(pk=u_id)
	u.is_active = True
	print u.username
	u.save()
	return render(request,"complaint_portal/login.html",{"msg":"Account Activated"})

def logout(request):
	'''logout normal users'''
	auth.logout(request)
	return HttpResponseRedirect(reverse('complaint_portal:index')) 

def forgot_password(request):
	"""
	This method is called whenever the user clicks on the forget continue button. This method checks if any such username is found in the database
	and if found then a reset password link is sent to user's mail id.
	"""
	if request.method == "POST":
		uname = request.POST.get("username","")
		if uname == "":
			return render(request,"complaint_portal/forgot_password.html",{"msg":False})
		else:	
			try:
				user = User.objects.get(username=uname)
				if len(user) != 1:
					#r_password = ''.join(random.choice(string.lowercase+string.digits) for i in range(8))
					#send_mail("Change Password","Password:"+r_password,"saurabh.finch@gmail.com",[user.email])
					return render(request,"complaint_portal/forgot_password.html",{"msg":False})
				
				return render(request,"complaint_portal/forgot_password.html",{"msg":True})
			except django.core.exceptions.ObjectDoesNotExist:
				return render(request,"complaint_portal/forgot_password.html",{"msg":False})
	else:
		return render(request,"complaint_portal/forgot_password.html")	

def complainform(request):
	'''complain form'''
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse("complaint_portal:index"))
	comp_user = UserInfos.objects.get(pk=request.user.id)
	if comp_user.ban_date < datetime.now and comp_user.ban_date != None:
		return render(request,"complaint_portal/complainform.html",{"places":places,"types":types,"msg":"You are banned","end_date":comp_user.ban_date})		
	if request.method == "POST" and request.user.is_authenticated():
		u = User.objects.get(pk=request.user.id)
		form = ComplainForm(request.POST,request.FILES,instance=u)
		if form.is_valid():			
			title = form.cleaned_data["title"]
			type_of_complain = form.cleaned_data["type_of_complain"]
			description = form.cleaned_data["description"]
			complain_address = form.cleaned_data["complain_address"]
			complain_image = form.cleaned_data["complain_image"]
			complain_place = form.cleaned_data["complain_place"] #locality
			print type_of_complain,title
			c = Complain(title=title,type_of_complain=type_of_complain,description=description,complain_address=complain_address,
				complain_image=complain_image,complain_place=complain_place,end_date=None)
			c.c_user = request.user
			c.save()
			return render(request,"complaint_portal/complainform.html",{"places":places,"types":types,"msg":"Complain Successfully Registered"})
		else:
			return render(request,"complaint_portal/complainform.html",{"places":places,"types":types,"msg":form.errors})
	else:
		return render(request,"complaint_portal/complainform.html",{"places":places,"types":types})


def all_complains(request):
	"""
	This function shows all the complaints excluding the complaints that were rejected by the middlemen.
	@Nidhi
	"""
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	complain_list = Complain.objects.exclude(govt_complain_status=2).order_by('-id')
	print complain_list
	return render(request,"complaint_portal/all_complain.html",{"complain_list":complain_list,"places":places,"types":types})


def hloc_filter(request,place_id):
	"""
	This function filters the complaints on the basis of place. Every place is assigned a 
	place_id and the complaints are filtered on the basis of place_id passed by the user.
	@Nidhi
	"""
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	p = LocalPlaces.objects.get(pk=place_id)
	print p.local_name
	complain_list = Complain.objects.filter(complain_place=p.local_name).order_by('id')
	return render(request,"complaint_portal/all_complain.html",{"complain_list":complain_list,"places":places,"types":types})


def htype_filter(request,type_id):
	"""
	This function filters the complaints on the basis of complaint type (Health , Sewage ,Water Problems).
	Every place is assigned a type_id and the complaints are filtered on the basis of type_id passed by the user.
	@Nidhi
	"""
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	t = Complain_type.objects.get(pk=type_id)
	complain_list = Complain.objects.filter(type_of_complain=t.name).order_by('id')
	return render(request,"complaint_portal/all_complain.html",{"complain_list":complain_list,"places":places,"types":types})

def sorted_complains(request,sorted_id):
	"""
	This function sorts the complaints on basis of complaint type and time of complaint. 
	sorted_id=1 is for sorting the complaints by the complaint date in ascending order.
	sorted_id=2 is for sorting the complaints by the complaint date in descending order.
	sorted_id=3 is for sorting the complaints by the complaint type in alphabetical order (A-Z).
	sorted_id=4 is for sorting the complaints by the complaint type in alphabetical order (Z-A).
	@Nidhi
	"""
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	if sorted_id == "1":
		complain_list = Complain.objects.order_by('complain_date')
	elif sorted_id == "2":
		print "f",sorted_id
		complain_list = Complain.objects.order_by('-complain_date')
	elif sorted_id == "3":
		complain_list = Complain.objects.order_by('type_of_complain')
	else:	
		complain_list = Complain.objects.order_by('-type_of_complain')
	return render(request,"complaint_portal/all_complain.html",{"complain_list":complain_list,"places":places,"types":types})

	
def all_complains_location(request,loc_id):
	"""
	This function filters the complaints on the basis of location.
	@Nidhi
	"""	
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	complain_list = Complain.objects.filter(complain_place=loc_id)
	return render(request,"complaint_portal/all_complain.html",{"complain_list":complain_list,"places":places,"types":types}) 

def details(request,complain_id):
	'''complain details page'''
	if request.method == "POST":
		content = request.POST.get("content","")
		name = request.user.username
		if request.user.is_staff or request.user.is_superuser:
			name += "(Admin)"
		print name
		c = Complain_usercomments.objects.create(content=content,comment_user=name,complain_id=complain_id)
		co = Complain.objects.get(pk=complain_id)
		print "abdff"
		if co.c_user.username != request.user.username:
			comm = Commentnotifications.objects.create(c_id=complain_id,u_id=request.user.id,c_title=co.title,
				u_name=name,comment=content)
	else:
		pass
	c_comments = Complain_usercomments.objects.filter(complain_id=complain_id)
	complain_detail = Complain.objects.get(pk=complain_id)
	return render(request,"complaint_portal/complain_detail.html",{"complain_detail":complain_detail,"comments":c_comments})


def userprofile(request):
	'''local feeds of logged in user'''
	print request.user.id
	print "dsg"
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse('complaint_portal:index'))
	print UserInfos.objects.all()
	u = UserInfos.objects.get(pk=request.user.id)   
	complain_feeds = Complain.objects.filter(complain_place=u.locality).exclude(govt_complain_status=2)
	print len(complain_feeds),"u"
	return render(request,"complaint_portal/complain_feeds.html",{"complain_feeds":complain_feeds})	

def mycomplains(request):
	'''showing list of user's own complains'''
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse('complaint_portal:index'))
	my_complain_feeds = request.user.complain_set.all()
	print "here"
	print len(my_complain_feeds)
	return render(request,"complaint_portal/complain_mine.html",{"my_complain_feeds":my_complain_feeds})

def user_complete(request,complain_id):
	'''marking complain as complete from user side'''
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse('complaint_portal:index'))
	complain = Complain.objects.get(pk=complain_id)
	if "complete" in request.POST:
		complain.user_complaint_status = 1
		complain.save()
		return HttpResponseRedirect(reverse('complaint_portal:mycomplains'))
	else:
		return HttpResponseRedirect(reverse('complaint_portal:user_notcomplete_status',args=(complain.id,)))			

def user_notcomplete_status(request,complain_id):
	'''marking complain as not complete from user side'''
	complain = Complain.objects.get(pk=complain_id)
	if request.method == "POST":
		description = request.POST.get("description","")
		complain.user_complain_status = 0
		complain.govt_complain_status = 5
		complain.user_complain_reason = description
		complain.save()
		return render(request,"complaint_portal/user_status_update.html",{"complain":complain,"msg":"Status conveyed to govt."})
	else:
		return render(request,"complaint_portal/user_status_update.html",{"complain":complain})	


def profile_update(request):
	'''updating user profile'''
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse('complaint_portal:index'))
	places = LocalPlaces.objects.all()
	profile_info = UserInfos.objects.get(pk=request.user.id)
	p_info = User.objects.get(pk=request.user.id)
	if request.method == "POST":
		form = UserInfoForm(request.POST)
		if form.is_valid():
			p_info.username = form.cleaned_data["username"]
			p_info.first_name = form.cleaned_data["firstname"]
			p_info.last_name = form.cleaned_data["lastname"]
			p_info.email = form.cleaned_data["email"]
			p_info.password = form.cleaned_data["password"]
			p_info.save()
			profile_info.address = request.POST.get("address","")
			profile_info.phone = request.POST.get("phone","")
			profile_info.locality = request.POST.get("locality","")
			profile_info.save()
			return render(request,"complaint_portal/profile_update.html",{"profile_info":profile_info,"msg":"Successfully Updated Profile",
				"places":places,"p_info":p_info})
		else:
			return render(request,"complaint_portal/profile_update.html",{"profile_info":profile_info,
				"p_info":p_info,"msg":form.errors,"places":places})				
	else:
		return render(request,"complaint_portal/profile_update.html",{"profile_info":profile_info,
			"p_info":p_info,"places":places})		

def complain_update(request,complain_id):
	'''updating complain info'''
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse('complaint_portal:index'))
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	print request.POST
	complain_info = Complain.objects.get(pk=complain_id)
	if "comment" in request.GET:
		print "ab"
		content = request.GET.get("content","")
		c = Complain_usercomments.objects.create(content=content,comment_user=request.user.username,complain_id=complain_id)
		return HttpResponseRedirect(reverse('complaint_portal:mycomplains'))
	elif request.method == "POST":
		form = ComplainForm(request.POST,request.FILES)
		if form.is_valid() and request.user.is_authenticated():
			complain_info.title = form.cleaned_data["title"]
			complain_info.type_of_complain = form.cleaned_data["type_of_complain"]
			complain_info.description = form.cleaned_data["description"]
			complain_info.complain_address = form.cleaned_data["complain_address"]
			complain_info.complain_image = form.cleaned_data["complain_image"]
			complain_info.complain_place = form.cleaned_data["complain_place"]
			complain_info.save()
			return render(request,"complaint_portal/complainform_update.html",{"complain_info":complain_info,"places":places,
				"types":types,"msg":"Complain Updated"})
		else:
			return render(request,"complaint_portal/complainform_update.html",{"complain_info":complain_info,"places":places,
				"types":types,"msg":form.errors})	
	else:
		return render(request,"complaint_portal/complainform_update.html",{"complain_info":complain_info,"places":places,
				"types":types})		

def ranking(request):
	'''dispalying user rank'''
	users_rank = UserInfos.objects.order_by('-total_upvotes')[:10]
	return render(request,"complaint_portal/ranking.html",{"users_rank":users_rank})

def complain_complete(request,complain_id):
	'''giving reason for user who is not satisfied'''
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse('complaint_portal:index'))
	complain_info = Complain.objects.get(pk=complain_id)
	if request.method=="POST":
		form = UpdateForm(request.POST)
		if form.is_valid() and request.user.is_authenticated():
			complain_info.user_complain_update = form.cleaned_data["user_complain_update"]
			complain_info.user_complain_reason = form.cleaned_data["user_complain_reason"]
			complain_info.save()
			return render(request,"complaint_portal/complain_complete.html",{"msg":"Successfully Updated Complaint","complain_info":complain_info})
		else:
			return render(request,"complaint_portal/complain_complete.html",{"msg":form.errors,"complain_info":complain_info})
	else:
		return render(request,"complaint_portal/complain_complete.html",{"complain_info":complain_info})

def upvote(request,complain_id):
	'''upvoting a complain'''
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse('complaint_portal:index'))
	complain_info = Complain.objects.get(pk=complain_id)
	if not request.user.userupvotestatus_set.values('upvote').filter(upvote=complain_info.id).exists():
		print "zxc"
		print request.user.userupvotestatus_set.values('upvote').filter(upvote=complain_info.id)
		complain_info.upvotes += 1
		complain_info.save()
		user_id = complain_info.c_user.id
		user_obj = UserInfos.objects.get(pk=user_id)
		user_obj.total_upvotes += 1
		user_obj.save()
		user_up_status = UserUpvoteStatus(user_upvote=request.user,upvote=complain_info.id)
		user_up_status.save()
		upvote_notification = Upvotenotification.objects.create(c_id=complain_id,u_id=request.user.id,
			c_title=complain_info.title,u_name=request.user.username)
		complain_list = Complain.objects.order_by('id')
		my_data = [complain_info.id,complain_info.upvotes]
		#return render(request,"complaint_portal/all_complain.html",{"complain_list":complain_list,"complain_id":complain_info.id})
		print complain_info.upvotes
		response_data = {}
		response_data['upvotes'] = complain_info.upvotes
		return HttpResponse(json.dumps(response_data),content_type="application/json")
	else:
		print "asfg"
		complain_list = Complain.objects.order_by('id')
		#return render(request,"complaint_portal/all_complain.html",{"complain_list":complain_list,"complain_id":complain_info.id})
		print complain_info.upvotes
		response_data = {}
		response_data['upvotes'] = complain_info.upvotes
		return HttpResponse(json.dumps(response_data),content_type="application/json")

def feed_upvote(request,complain_id):
	'''not used now'''
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse('complaint_portal:index'))
	complain_info = Complain.objects.get(pk=complain_id)
	if not request.user.userupvotestatus_set.values('upvote').filter(upvote=complain_info.id).exists():
		print request.user.userupvotestatus_set.values('upvote').filter(upvote=complain_info.id)
		complain_info.upvotes += 1
		complain_info.save()
		user_id = complain_info.c_user.id
		user_obj = UserInfos.objects.get(pk=user_id)
		user_obj.total_upvotes += 1
		user_obj.save()
		user_up_status = UserUpvoteStatus(user_upvote=request.user,upvote=complain_info.id)
		user_up_status.save()
		complain_list = Complain.objects.order_by('id')
		my_data = [complain_info.id,complain_info.upvotes]
		return HttpResponseRedirect(reverse('complaint_portal:userprofile'))
	else:
		return HttpResponseRedirect(reverse('complaint_portal:userprofile'))



#MIDDLEMEN	
def middlemen(request):
	'''middlemen's main view'''
	if not request.user.is_authenticated or not request.user.is_staff:
		return HttpResponseRedirect(reverse('complaint_portal:mlogin'))
	complain=Complain.objects.filter(Q(govt_complain_status=0) | Q(forum_visible=1)).order_by('-upvotes')
	types = Complain_type.objects.all()
	places = LocalPlaces.objects.all()
	return render(request,"complaint_portal/middlemen.html",{"complain":complain,"places":places,"types":types})

def mlogin(request):
	'''not used now'''
	complain=Complain.objects.filter(govt_complain_status=0)
	places = LocalPlaces.objects.all()
	if request.method == "POST":
		username = request.POST.get("username","")
		password = request.POST.get("password","")
		user = auth.authenticate(username=username,password=password)
		if user is not None and user.is_staff:
			auth.login(request,user)
			#return render(request,"complaint_portal/middlemen.html",{"complain":complain,"places":places})  #change login to userprofilename on homepage
			return HttpResponseRedirect(reverse('complaint_portal:middlemen'))
		else:
			return render(request,"complaint_portal/mlogin.html",{"msg":"Username and Password combination incorrect"})
	else:
		return render(request,"complaint_portal/mlogin.html")			

def mlogout(request):
	'''logging out middlemen'''
	auth.logout(request)
	return HttpResponseRedirect(reverse('complaint_portal:index'))

def mloc_filter(request,loc_id):
	'''filter by location'''
	if not request.user.is_authenticated or not request.user.is_staff:
		return HttpResponseRedirect(reverse('complaint_portal:mlogin'))
	p = LocalPlaces.objects.get(pk=loc_id)
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	complain = Complain.objects.filter(govt_complain_status=0 | Q(forum_visible=1)).filter(complain_place=p.local_name)
	return render(request,"complaint_portal/middlemen.html",{"complain":complain,"places":places,"types":types})


def mtype_filter(request,type_id):
	'''filter by type'''
	if not request.user.is_authenticated or not request.user.is_staff:
		return HttpResponseRedirect(reverse('complaint_portal:mlogin'))
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	t = Complain_type.objects.get(pk=type_id)
	complain = Complain.objects.filter(govt_complain_status=0 | Q(forum_visible=1)).filter(type_of_complain=t.name)
	return render(request,"complaint_portal/middlemen.html",{"complain":complain,"places":places,"types":types})

def forward_reject(request):
	'''rejecting or forwarding complain to govt'''
	if not request.user.is_authenticated or not request.user.is_staff:
		return HttpResponseRedirect(reverse('complaint_portal:mlogin'))
	c_list = request.POST.getlist("sel_complain")
	if "forward" in request.POST:
		for c in c_list:
			c_obj = Complain.objects.get(pk=c)
			c_obj.govt_complain_status=1
			comp_user = UserInfos.objects.get(pk=c_obj.c_user.id)
			comp_user.total_upvotes += 5
			comp_user.save()
			status = Statusnotifications.objects.create(c_id=c,status=1,c_title=c_obj.title)
			c_obj.save()
			#send_mail("Complain Accepted"+c.title,"You will be notified about further actions","saurabh.finch@gmail.com",[c.c_user.email])
	else:
		for c in c_list:
			c_obj = Complain.objects.get(pk=c)
			c_obj.govt_complain_status=2
			comp_user = UserInfos.objects.get(pk=c_obj.c_user.id)
			comp_user.total_upvotes -= 5
			u_obj = User.objects.get(pk=comp_user.id)
			num_complains = len(u_obj.complain_set.all())
			if comp_user.total_upvotes < 0 and num_complains>3:
				comp_user.ban_date = (datetime.now()+timedelta(days=7))
			comp_user.save()
			status = Statusnotifications.objects.create(c_id=c,status=2,c_title=c_obj.title)
			reason = request.POST.get("reason","")
			c_obj.rejection_reason=int(reason)
			c_obj.save()
			#send_mail("Complain rejected"+c.title,"Your complain got rejected.See FAQ for reasons why complain can be rejected","saurabh.finch@gmail.com",[c.c_user.email])
	complain = Complain.objects.filter(govt_complain_status=0)
	types = Complain_type.objects.all()
	places = LocalPlaces.objects.all()				
	return HttpResponseRedirect(reverse('complaint_portal:middlemen'))



#GOVT EMPLOYEE	
def govtadmin(request):
	'''If government admin is logged in Successfully,
	Load GovernmentInfo(His respective department), department, complain objects.
	Render these object to govtadmin.html 
	@Amit Masani'''
	if not request.user.is_authenticated or not request.user.is_superuser:
		return HttpResponseRedirect(reverse('complaint_portal:glogin'))		
	print request.user
	c = GovtUserInfo.objects.get(pk=request.user.id)
	c_type = c.department
	complain=Complain.objects.filter(Q(govt_complain_status=6) |Q(govt_complain_status=1) | Q(govt_complain_status=5) | Q(govt_complain_status=4) | Q(forum_visible=1)).filter(type_of_complain=c_type).order_by('-upvotes')
	print len(complain)
	types = Complain_type.objects.all()
	places=LocalPlaces.objects.all()
	return render(request,"complaint_portal/govtadmin.html",{"complain":complain,"types":types,"places":places})

def glogin(request):
	'''This function login the government admin.
	It checks usrname & password combination.
	If it fails then it redirects it to login page again. 	
	@Amit Masani'''
	if request.method == "POST":
		username = request.POST.get("username","")
		password = request.POST.get("password","")
		user = auth.authenticate(username=username,password=password)
		if user is not None and user.is_superuser:
			auth.login(request,user)
			return HttpResponseRedirect(reverse("complaint_portal:govtadmin")) 
		else:
			return render(request,"complaint_portal/glogin.html",{"msg":"Username and Password combination incorrect "})
	else:
		return render(request,"complaint_portal/glogin.html")				

def gloc_filter(request,loc_id):
	'''This filter is used to filter Complain Location wise. 
	We check if Government user is logged in & he is super user.
	If he is not then Redirect it to Government Login Page Again.
	We select our desired Loaction object & Complain type object.
	We select complain with that perticular Location from Complain status 1,4,5.
	It renders the request to govtadmin.html with complain places & types object.
	@Amit Masani'''
	if not request.user.is_authenticated or not request.user.is_superuser:
		return HttpResponseRedirect(reverse('complaint_portal:glogin'))
	l = LocalPlaces.objects.get(pk=loc_id)
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	complain = Complain.objects.filter(Q(forum_visible=1) | Q(govt_complain_status=6) | Q(govt_complain_status=1) | Q(govt_complain_status=5) | Q(govt_complain_status=4)).filter(complain_place=l.local_name)
	return render(request,"complaint_portal/govtadmin.html",{"complain":complain,"places":places,"types":types})

def gtype_filter(request,type_id):
	'''This filter is used to filter Complain type wise.	
	We select our desired Complaint type object & Location object.
	We select complain with that perticular Complain Type from Complain status 1,4,5.
	@Amit Masani'''
	if not request.user.is_authenticated or not request.user.is_superuser:
		return HttpResponseRedirect(reverse('complaint_portal:glogin'))
	c = Complain_type.objects.get(pk=type_id)
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	complain = Complain.objects.filter(Q(forum_visible=1) | Q(govt_complain_status=6) |Q(govt_complain_status=1) | Q(govt_complain_status=5) | Q(govt_complain_status=4)).filter(type_of_complain=c.name)
	return render(request,"complaint_portal/govtadmin.html",{"complain":complain,"places":places,"types":types})

def gdays_filter(request):
	'''This filter is used to filter Complain in which days to add.
	We filter the complains whose day to complete is yet to add.	
	@Amit Masani'''
	if not request.user.is_authenticated or not request.user.is_superuser:
		return HttpResponseRedirect(reverse('complaint_portal:glogin'))
	complain = Complain.objects.filter(Q(forum_visible=1) | Q(govt_complain_status=1))
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	return render(request,"complaint_portal/govtadmin.html",{"complain":complain,"places":places,"types":types})

def gcomplete_filter(request):
	'''This filter is used to filter Complain which are completed.
	We filter the complains whose end date is set or are resent for review by user.	
	@Amit Masani'''
	if not request.user.is_authenticated or not request.user.is_superuser:
		return HttpResponseRedirect(reverse('complaint_portal:glogin'))
	complain = Complain.objects.filter(Q(forum_visible=1) | Q(govt_complain_status=6) |Q(govt_complain_status=4) | Q(govt_complain_status=5))
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	return render(request,"complaint_portal/govtadmin.html",{"complain":complain,"places":places,"types":types})

def glogout(request):
	'''This function logout the government admin.	
	@Amit Masani'''
	auth.logout(request)
	return HttpResponseRedirect(reverse('complaint_portal:index'))

def days_or_complete(request):
	'''If Complain is reviewed by government admin,
	Set its status to 4 & update end date. If it is completed then set it to 3.
	save it to database.
	@Amit Masani'''
	if not request.user.is_authenticated or not request.user.is_superuser:
		return HttpResponseRedirect(reverse('complaint_portal:glogin'))
	c = request.POST
	print c
	if "complain_id" in request.POST:
		c_id = request.POST["complain_id"]
		complain = Complain.objects.get(pk=c_id)
		num_days = request.POST.getlist("num_days")
		for i in num_days:
			if i!='':
				#complain.days_to_solve = i
				#complain.end_date = (datetime.now()+timedelta(days=int(i)))
				complain.end_date = i
				print complain.end_date,i
				#complain.govt_complain_status = 4
				if complain.govt_complain_status == 4:
					complain.govt_complain_status = 6
					status = Statusnotifications.objects.create(c_id=c_id,status=6,c_title=complain.title)
				elif complain.govt_complain_status == 6:
					complain.govt_complain_status = 6
					status = Statusnotifications.objects.create(c_id=c_id,status=6,c_title=complain.title)
				else:
					complain.govt_complain_status = 4		
					status = Statusnotifications.objects.create(c_id=c_id,status=4,c_title=complain.title)
				complain.save()
				print complain
	else:
		c_list = request.POST.getlist("sel_complain")
		for c in c_list:
			c_obj = Complain.objects.get(pk=c)
			c_obj.govt_complain_status = 3
			c_obj.forum_visible = 0            
			status = Statusnotifications.objects.create(c_id=c,status=3,c_title=c_obj.title)
			c_obj.save()
			
	return HttpResponseRedirect(reverse("complaint_portal:govtadmin"))

#SysAdmin
def super_login(request):
	'''sysadmin login'''
	if request.method == "POST":
		username = request.POST.get("username","")
		password = request.POST.get("password","")
		user = auth.authenticate(username=username,password=password)
		if user is not None and user.is_superuser and user.is_staff and user.is_active:
			auth.login(request,user)
			return HttpResponseRedirect(reverse("complaint_portal:adminregister")) 
		else:
			return render(request,"complaint_portal/adminlogin.html",{"msg":"Username and Password combination incorrect "})
	else:
		return render(request,"complaint_portal/adminlogin.html")				

def adminregister(request):
	'''registering middlemen and govt employee'''
	if not request.user.is_authenticated or not request.user.is_superuser or not request.user.is_staff or not request.user.is_active:
		return HttpResponseRedirect(reverse("complaint_portal:super_login"))
	
	types = Complain_type.objects.all()
	if request.method == "POST":
		form = UserInfoForm(request.POST)
		print request.POST
		if form.is_valid():
			username = form.cleaned_data["username"]
			firstname = form.cleaned_data["first_name"]
			lastname = form.cleaned_data["last_name"]
			email = form.cleaned_data["email"]
			password = form.cleaned_data["password"] #confirm_password check on frontend
			address	= request.POST.get("address","")
			phone = request.POST.get("phone","")
			department = request.POST.get("department","")
			user = User.objects.create_user(username=username,first_name=firstname,last_name=lastname,email=email,password=password)
			position = request.POST.get("position","")
			print firstname,lastname,position
			#user.is_active = False
			if int(position)==1:
				user.is_staff=True
			else:
				user.is_superuser=True
			user.save()
			userinfo = GovtUserInfo.objects.create(id=user.id,user_id=user.id,address=address,phone=phone,department=department)
			userinfo.save()		
			#url = "http://localhost:8000/complaint_portal/" + "activate/" + str(user.id)
			#send_mail("Activate your account",url,"saurabh.finch@gmail.com",[user.email])
			return render(request,"complaint_portal/adminregister.html",{"types":types,"msg":"Account Registered."})
		else:
			return render(request,"complaint_portal/adminregister.html",{"msg":form.errors,"types":types})
	else:
		return render(request,"complaint_portal/adminregister.html",{"types":types})			

		
#MIDDLEMEN and GOVT EMPLOYEE			
def userprofile_admin(request,u_id):
	'''user profile visible to middlemen and govt.'''
	print u_id
	userinfo = UserInfos.objects.get(pk=u_id)
	u_info = User.objects.get(pk=u_id)
	return render(request,"complaint_portal/userprofile_admin.html",{"userinfo":userinfo,"u_info":u_info})

def send_mail_user(request,u_id):
	'''send mail to user'''
	if request.method == "POST":
		content = request.POST.get("content","")
		send_mail("Some questions",content,"saurabh.finch@gmail.com",[userinfo.email])
		return render(request,"complaint_portal/userprofile_admin.html",{"userinfo":userinfo})
	else:
		return HttpResponseRedirect(reverse("complaint_portal:userprofile_admin"))	
			

def dforum(request,complain_id):
	'''discussion forum for middlemen and govt.'''
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse("complaint_portal:mlogin"))
	complain = Complain.objects.get(pk=complain_id)
	try:
		c_comments = Complain_comments.objects.filter(complain_id=complain_id) 
	except Complain_comments.DoesNotExist:
		c_comments = None
	if request.method=="POST":
		content = request.POST.get("content","")
		c = Complain_comments.objects.create(content=content,comment_user=request.user.username,complain_id=complain_id)
		c_comments = Complain_comments.objects.filter(complain_id=complain_id)
		complain.forum_visible = 1
		complain.save() 
		return render(request,"complaint_portal/dforum.html",{"complain":complain,"comments":c_comments})
	else:
		return render(request,"complaint_portal/dforum.html",{"complain":complain,"comments":c_comments})

def comment(request,complain_id):
	'''comments on complain'''
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse('complaint_portal:index'))
	print request.GET
	print "bdf"
	content = request.GET.get("content","")
	name = request.user.username
	if request.user.is_staff or request.user.is_superuser:
		name += "(Admin)"
	print name
	c = Complain_usercomments.objects.create(content=content,comment_user=name,complain_id=complain_id)
	co = Complain.objects.get(pk=complain_id)
	print "bdff"
	if co.c_user.username != request.user.username:
		comm = Commentnotifications.objects.create(c_id=complain_id,u_id=request.user.id,c_title=co.title,
			u_name=name,comment=content)
	
	response_data = {}
	response_data['done'] = "Update Added"
	return HttpResponse(json.dumps(response_data),content_type="application/json")
	
def displaycomment(request,complain_id):
	'''displaying comments'''
	comments = Complain_usercomments.objects.filter(complain_id=complain_id)
	print len(comments)
	return render(request,"complaint_portal/displaycomment.html",{"comments":comments})	

def upvote_notification(request):
	'''notification system for all upvotes,status changes and comments'''
	c_set = request.user.complain_set.values('id')
	print len(c_set),"dhtsdfj"
	upvote = []
	comment = []
	status = []
	for c in c_set:
		print c['id']
		u_not = Upvotenotification.objects.filter(c_id=c['id']).filter(Q(read=0) | Q(read=1)).order_by('u_date')
		print u_not.values()
		if u_not.values():
			upvote.append(u_not)

	for c in c_set:
		c_not = Commentnotifications.objects.filter(c_id=c['id']).filter(Q(read=0) | Q(read=1)).order_by('c_date')
		print c_not.values()
		if c_not.values():
			comment.append(c_not)

	for c in c_set:
		s_not = Statusnotifications.objects.filter(c_id=c['id']).filter(Q(read=0) | Q(read=1)).order_by('s_date')
		print s_not.values()
		if s_not.values():
			status.append(s_not)		
	print upvote	
	print comment
	print status
	num = len(upvote)+len(comment)+len(status)
	return render(request,"complaint_portal/notification.html",{"upvote":upvote,"comment":comment,
		"status":status})	

def num_notification(request):
	'''displays no. of notifications'''
	c_set = request.user.complain_set.values('id')
	print len(c_set),"dhtsdfj"
	upvote = []
	comment = []
	status = []
	num = 0
	for c in c_set:
		print c['id']
		u_not = Upvotenotification.objects.filter(c_id=c['id']).filter(Q(read=0) | Q(read=1))
		print u_not.values()
		num += u_not.count()
		if u_not.values():
			upvote.append(u_not)

	for c in c_set:
		c_not = Commentnotifications.objects.filter(c_id=c['id']).filter(Q(read=0) | Q(read=1))
		print c_not.values()
		print c_not.count()
		num += c_not.count()
		if c_not.values():
			comment.append(c_not)

	for c in c_set:
		s_not = Statusnotifications.objects.filter(c_id=c['id']).filter(Q(read=0) | Q(read=1))
		num += s_not.count()
		print s_not.values()
		if s_not.values():
			status.append(s_not)		
	print upvote	
	print comment
	print status
	response_data = {}
	response_data['num'] = num
	return HttpResponse(json.dumps(response_data),content_type="application/json")
	

def readupvote(request,id):
	'''mark upvote as read'''
	obj = Upvotenotification.objects.get(id=id)
	obj.read = 1
	obj.save()
	response_data = {}
	response_data['done'] = True
	return HttpResponse(json.dumps(response_data),content_type="application/json")

def delupvote(request,id):
	'''mark upvote as delete'''
	obj = Upvotenotification.objects.get(id=id)
	obj.delete()
	response_data = {}
	response_data['done'] = True
	return HttpResponse(json.dumps(response_data),content_type="application/json")
	
def readcomment(request,id):
	'''mark comment as read'''
	obj = Commentnotifications.objects.get(id=id)
	obj.read = 1;
	obj.save()
	response_data = {}
	response_data['done'] = True
	return HttpResponse(json.dumps(response_data),content_type="application/json")
	
def delcomment(request,id):
	'''mark comment as delete'''
	c = Commentnotifications.objects.get(id=id)
	c.delete()
	response_data = {}
	response_data['done'] = True
	return HttpResponse(json.dumps(response_data),content_type="application/json")
	
def readstatus(request,id):
	'''mark status as read'''
	obj = Statusnotifications.objects.get(id=id)
	obj.read = 1;
	obj.save()
	response_data = {}
	response_data['done'] = True
	return HttpResponse(json.dumps(response_data),content_type="application/json")
	
def delstatus(request,id):
	'''mark status as delete'''
	c = Statusnotifications.objects.get(id=id)
	c.delete()
	response_data = {}
	response_data['done'] = True
	return HttpResponse(json.dumps(response_data),content_type="application/json")

def user_public_profile(request,id):
	'''user's public profile'''
	u_info = User.objects.get(id=id)
	userinfo = UserInfos.objects.get(id=id)
	return render(request,"complaint_portal/user_public_profile.html",{"u_info":u_info,"userinfo":userinfo})