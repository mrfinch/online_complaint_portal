from django.shortcuts import render
from complaint_portal.models import *
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse 
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
			return HttpResponseRedirect(reverse('complaint_portal:index'))
		else:
			return render(request,"complaint_portal/login.html",{"msg":"Username and Password combination incorrect OR Account not activated by email"})
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
	return HttpResponseRedirect(reverse('complaint_portal:login')) 

def complainform(request):
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse("complaint_portal:login"))
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
	complain_list = Complain.objects.order_by('id')
	return render(request,"complaint_portal/all_complain.html",{"complain_list":complain_list})

def sorted_complains(request,sorted_id):
	print "hp"
	if sorted_id == "1":
		complain_list = Complain.objects.order_by('complain_date')
	elif sorted_id == "2":
		print "f",sorted_id
		complain_list = Complain.objects.order_by('-complain_date')
	elif sorted_id == "3":
		complain_list = Complain.objects.order_by('type_of_complain')
	else:	
		complain_list = Complain.objects.order_by('-type_of_complain')
	return render(request,"complaint_portal/all_complain.html",{"complain_list":complain_list})
		
def all_complains_location(request,loc_id):
	complain_list = Complain.objects.filter(complain_place=loc_id)
	return render(request,"complaint_portal/all_complain.html",{"complain_list":complain_list}) 

def details(request,complain_id):
	complain_detail = Complain.objects.get(pk=complain_id)
	return render(request,"complaint_portal/complain_detail.html",{"complain_detail":complain_detail})


def userprofile(request):
	#get news feed of local complains of user
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse('complaint_portal:login'))
	u = UserInfos.objects.get(pk=request.user.id)   
	complain_feeds = Complain.objects.filter(complain_place=u.locality)
	print len(complain_feeds),"u"
	return render(request,"complaint_portal/complain_feeds.html",{"complain_feeds":complain_feeds})	

def mycomplains(request):
	#in rendering html check if status is accepted or not and provide update button
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse('complaint_portal:login'))
	my_complain_feeds = request.user.complain_set.all()
	print len(my_complain_feeds),"here"
	return render(request,"complaint_portal/complain_mine.html",{"my_complain_feeds":my_complain_feeds})

def profile_update(request):
	print "h"
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse('complaint_portal:login'))
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
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse('complaint_portal:login'))
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
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
			return render(request,"complaint_portal/complainform_update.html",{"complain_info":complain_info,"places":places,
				"types":types,"msg":"Complain Updated"})
		else:
			return render(request,"complaint_portal/complainform_update.html",{"complain_info":complain_info,"places":places,
				"types":types,"msg":form.errors})	
	else:
		return render(request,"complaint_portal/complainform_update.html",{"complain_info":complain_info,"places":places,
				"types":types})		

def ranking(request):
	users_rank = UserInfos.objects.order_by('-total_upvotes')[:10]
	return render(request,"complaint_portal/ranking.html",{"users_rank":users_rank})

def complain_complete(request,complain_id):
	if not request.user.is_authenticated or not request.user.is_active:
		return HttpResponseRedirect(reverse('complaint_portal:login'))
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
		return render(request,"complaint_portal/all_complain.html",{"complain_list":complain_list,"complain_id":complain_info.id,
			"new_upvotes":complain_info.upvotes})
		'''print my_data
		return HttpResponse(my_data)'''
	else:
		complain_list = Complain.objects.order_by('id')
		return render(request,"complaint_portal/all_complain.html",{"complain_list":complain_list,"complain_id":complain_info.id})
		'''
		print "ge"
		return HttpResponse("already upvoted")
		'''

def middlemen(request):
	if not request.user.is_authenticated or not request.user.is_staff:
		return HttpResponseRedirect(reverse('complaint_portal:mlogin'))
	complain=Complain.objects.filter(govt_complain_status=0)
	types = Complain_type.objects.all()
	places = LocalPlaces.objects.all()
	return render(request,"complaint_portal/middlemen.html",{"complain":complain,"places":places,"types":types})

def mlogin(request):
	print "dkjhkjh"
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
	auth.logout(request)
	return HttpResponseRedirect(reverse('complaint_portal:mlogin'))

def mloc_filter(request,loc_id):
	print "ht"
	if not request.user.is_authenticated or not request.user.is_staff:
		return HttpResponseRedirect(reverse('complaint_portal:mlogin'))
	p = LocalPlaces.objects.get(pk=loc_id)
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	complain = Complain.objects.filter(govt_complain_status=0).filter(complain_place=p.local_name)
	return render(request,"complaint_portal/middlemen.html",{"complain":complain,"places":places,"types":types})


def mtype_filter(request,type_id):
	print "hy"
	if not request.user.is_authenticated or not request.user.is_staff:
		return HttpResponseRedirect(reverse('complaint_portal:mlogin'))
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	t = Complain_type.objects.get(pk=type_id)
	complain = Complain.objects.filter(govt_complain_status=0).filter(type_of_complain=t.name)
	return render(request,"complaint_portal/middlemen.html",{"complain":complain,"places":places,"types":types})

def forward_reject(request):
	print "vd"#for middlemen
	if not request.user.is_authenticated or not request.user.is_staff:
		return HttpResponseRedirect(reverse('complaint_portal:mlogin'))
	c_list = request.POST.getlist("sel_complain")
	if "forward" in request.POST:
		for c in c_list:
			c_obj = Complain.objects.get(pk=c)
			c_obj.govt_complain_status=1
			c_obj.save()
			#send_mail("Complain Accepted"+c.title,"You will be notified about further actions","saurabh.finch@gmail.com",[c.c_user.email])
	else:
		for c in c_list:
			c_obj = Complain.objects.get(pk=c)
			c_obj.govt_complain_status=2
			c_obj.save()
			#send_mail("Complain rejected"+c.title,"Your complain got rejected.See FAQ for reasons why complain can be rejected","saurabh.finch@gmail.com",[c.c_user.email])
	complain = Complain.objects.filter(govt_complain_status=0)
	types = Complain_type.objects.all()
	places = LocalPlaces.objects.all()				
	return HttpResponseRedirect(reverse('complaint_portal:middlemen'))
	
def govtadmin(request):
	complain=Complain.objects.filter(govt_complain_status=1)
	print len(complain)
	types = Complain_type.objects.all()
	places=LocalPlaces.objects.all()
	return render(request,"complaint_portal/govtadmin.html",{"complain":complain,"types":types,"places":places})

def glogin(request):
	complain=Complain.objects.filter(govt_complain_status=1)
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
	l = LocalPlaces.objects.get(pk=loc_id)
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	complain = Complain.objects.filter(govt_complain_status=1).filter(complain_place=l.local_name)
	return render(request,"complaint_portal/govtadmin.html",{"complain":complain,"places":places,"types":types})

def gtype_filter(request,type_id):
	c = Complain_type.objects.get(pk=type_id)
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	complain = Complain.objects.filter(govt_complain_status=1).filter(type_of_complain=c.name)
	return render(request,"complaint_portal/govtadmin.html",{"complain":complain,"places":places,"types":types})

def gdays_filter(request):
	complain = Complain.objects.filter(govt_complain_status=1).filter(days_to_solve=-1)
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	return render(request,"complaint_portal/govtadmin.html",{"complain":complain,"places":places,"types":types})

def gcomplete_filter(request):
	complain = Complain.objects.filter(govt_complain_status=1).filter(days_to_solve__gte=0)
	places = LocalPlaces.objects.all()
	types = Complain_type.objects.all()
	return render(request,"complaint_portal/govtadmin.html",{"complain":complain,"places":places,"types":types})

def glogout(request):
	auth.logout(request)
	return HttpResponseRedirect(reverse('complaint_portal:glogin'))

def days_or_complete(request):
	c = request.POST
	print c
	if "complain_id" in request.POST:
		c_id = request.POST["complain_id"]
		complain = Complain.objects.get(pk=c_id)
		num_days = request.POST.getlist("num_days")
		for i in num_days:
			if i!='':
				complain.days_to_solve = i
				complain.save()
	else:
		c_list = request.POST.getlist("sel_complain")
		for c in c_list:
			c_obj = Complain.objects.get(pk=c)
			c_obj.govt_complain_status = 3            #complete
			c_obj.save()
			
	return HttpResponseRedirect(reverse("complaint_portal:govtadmin"))

def adminregister(request):
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
			user.is_active = True
			user.save()
			userinfo = UserInfos.objects.create(id=user.id,username=username,firstname=firstname,lastname=lastname,email=email,password=password,
				address=address,phone=phone,locality=locality)
			#url = "http://localhost:8000/complaint_portal/" + "activate/" + str(user.id)
			#send_mail("Activate your account",url,"saurabh.finch@gmail.com",[user.email])
			return render(request,"complaint_portal/adminregister.html",{"places":places,"msg":"Account Registered."})
		else:
			return render(request,"complaint_portal/adminregister.html",{"msg":form.errors,"places":places})
	else:
		return render(request,"complaint_portal/adminregister.html",{"places":places})			

