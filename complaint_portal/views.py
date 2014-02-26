from django.shortcuts import render
from complaint_portal.models import *
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
# Create your views here.

def index(request):
	current_complains = Complain.objects.order_by('complain_date')[:5]
	return render(request,"complaint_portal/index.html",{"current_complains":current_complains})

def register(request):
	places = LocalPlaces.objects.all()
	if request.method == "POST":
		form = UserInfoForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data["username"]
			firstname = form.cleaned_data["firstname"]
			lastname = form.cleaned_data["lastname"]
			email = form.cleaned_data["email"]
			password = form.cleaned_data["password"] #confirm_password check on frontend
			address	= form.cleaned_data["address"]
			phone = form.cleaned_data["phone"]
			locality = form.cleaned_data["locality"]
			user = User.objects.create_user(username=username,first_name=firstname,last_name=lastname,email=email,password=password)
			user.is_active = False
			user.save()
			userinfo = UserInfos.objects.create(id=user.id,username=username,firstname=firstname,lastname=lastname,email=email,password=password,
				address=address,phone=phone,locality=locality)
			url = "http://localhost:8000/complaint_portal/" + "activate/" + str(user.id)
			send_mail("Activate your account",url,"saurabh.finch@gmail.com",[user.email])
			return render(request,"complaint_portal/register.html",{"places":places,"msg":"Account Registered. Activate it by clicking link sent to your registeredemail"})
		else:
			return render(request,"complaint_portal/register.html",{"msg":form.errors,"places":places})
	else:
		return render(request,"complaint_portal/register.html",{"places":places})			

def login(request):
	print "daf"
	if request.method == "POST":
		username = request.POST.get("username","")
		password = request.POST.get("password","")
		user = auth.authenticate(username=username,password=password)
		if user is not None and user.is_active:
			auth.login(request,user)
			return render(request,"complaint_portal/index.html")  #change login to userprofilename on homepage
		else:
			return render(request,"complaint_portal/login.html",{"msg":"Username and Password combination incorrect"})
	else:
		return render(request,"complaint_portal/login.html")			

def activate(request,u_id):
	u = User.objects.get(pk=u_id)
	u.is_active = True
	print u.username
	u.save()
	return render(request,"complaint_portal/login.html",{"msg":"Account Activated"})

def logout(request):
	auth.logout(request)
	return render(request,"complaint_portal/index.html")  #change username to login on homepage

def complainform(request):
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
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
				complain_image=complain_image,complain_place=complain_place)
			c.c_user = request.user
			c.save()
			return render(request,"complaint_portal/complainform.html",{"places":places,"types":types,"msg":"Complain Successfully Registered"})
		else:
			return render(request,"complaint_portal/complainform.html",{"places":places,"types":types,"msg":form.errors})
	else:
		return render(request,"complaint_portal/complainform.html",{"places":places,"types":types})

def all_complains(request):
	complain_list = Complain.objects.all()
	return render(request,"complaint_portal/all_complain.html",{"complain_list":complain_list})

def all_complains_location(request,loc_id):
	complain_list = Complain.objects.filter(complain_place=loc_id)
	return render(request,"complaint_portal/all_complain.html",{"complain_list":complain_list}) 

def details(request,complain_id):
	complain_detail = Complain.objects.get(pk=complain_id)
	return render(request,"complaint_portal/complain_detail.html",{"complain_detail":complain_detail})


def userprofile(request):
	#get news feed of local complains of user
	u = UserInfos.objects.get(pk=request.user.id)   
	complain_feeds = Complain.objects.filter(complain_place=u.locality)
	print len(complain_feeds),"u"
	return render(request,"complaint_portal/complain_feeds.html",{"complain_feeds":complain_feeds})	

def mycomplains(request):
	#in rendering html check if status is accepted or not and provide update button
	my_complain_feeds = request.user.complain_set.all()
	print len(my_complain_feeds),"here"
	return render(request,"complaint_portal/complain_mine.html",{"my_complain_feeds":my_complain_feeds})

def profile_update(request):
	print "h"
	places = LocalPlaces.objects.all()
	profile_info = UserInfos.objects.get(pk=request.user.id)
	if request.method == "POST":
		form = UserInfoForm(request.POST)
		if form.is_valid():
			profile_info.username = form.cleaned_data["username"]
			profile_info.firstname = form.cleaned_data["firstname"]
			profile_info.lastname = form.cleaned_data["lastname"]
			profile_info.email = form.cleaned_data["email"]
			profile_info.password = form.cleaned_data["password"]
			profile_info.address = form.cleaned_data["address"]
			profile_info.locality = form.cleaned_data["locality"]
			profile_info.phone = form.cleaned_data["phone"]
			profile_info.save()
			return render(request,"complaint_portal/profile_update.html",{"profile_info":profile_info,"msg":"Successfully Updated Profile","places":places})
		else:
			return render(request,"complaint_portal/profile_update.html",{"profile_info":profile_info,"msg":form.errors,"places":places})				
	else:
		return render(request,"complaint_portal/profile_update.html",{"profile_info":profile_info,"places":places})		

def complain_update(request,complain_id):
	#can be done only before it is reviewed by middlemen.In mycomplains provide option of update if status is 0
	complain_info = Complain.objects.get(pk=complain_id)
	if request.method == "POST":
		form = ComplainForm(request.POST,request.FILES)
		if form.is_valid() and request.user.is_authenticated():
			complain_info.title = form.cleaned_data["title"]
			complain_info.type_of_complain = form.cleaned_data["complain_type"]
			complain_info.description = form.cleaned_data["description"]
			complain_info.complain_address = form.cleaned_data["complain_address"]
			complain_info.complain_image = form.cleaned_data["complain_image"]
			complain_info.complain_place = form.cleaned_data["complain_place"]
			complain_info.save()
			return render(request,"complaint_portal/compalinform_update.html",{"complain_info":complain_info,"msg":"Complain Updated"})
		else:
			return render(request,"complaint_portal/compalinform_update.html",{"complain_info":complain_info,"msg_dict":form.errors.as_data()})	
	else:
		return render(request,"complaint_portal/compalinform_update.html",{"complain_info":complain_info})		

def ranking(request):
	users_rank = UserInfos.objects.order_by('total_upvotes')[:10]
	return render(request,"complaint_portal/ranking.html",{"users_rank":users_rank})

def complain_complete(request,complain_id):
	complain_info = Complain.objects.get(pk=complain_id)
	if request.method=="POST":
		form = UpdateForm(request.POST)
		if form.is_valid() and request.user.is_authenticated():
			complain_info.user_complain_update = form.cleaned_data["user_complain_update"]
			complain_info.user_complain_reason = form.cleaned_data["user_complain_reason"]
			complain_info.save()
			return render(request,"complaint_portal/complain_complete.html",{"msg":"Successfully Updated Complaint","complain_info":complain_info})
		else:
			return render(request,"complaint_portal/complain_complete.html",{"msg_dict":form.errors.as_data(),"complain_info":complain_info})
	else:
		return render(request,"complaint_portal/complain_complete.html",{"complain_info":complain_info})					