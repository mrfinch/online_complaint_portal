'''Creating database tables
@Saurabh and @Dhruv'''

from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from datetime import datetime
from django.contrib.auth.models import User


def content_file_name(instance,filename):
	'''uploaded image's path'''
	print instance
	return '/'.join(["complaint_portal/images",instance.c_user.username,filename])

class Complain(models.Model):
	c_user = models.ForeignKey(User)
	title = models.CharField(max_length=50)
	type_of_complain = models.CharField(max_length=50)  #??????
	description = models.TextField()
	complain_address = models.TextField()
	complain_place = models.CharField(max_length=50)   #locality
	complain_image = models.ImageField(upload_to=content_file_name,blank=True,null=True)
	complain_date = models.DateTimeField(default=datetime.now)
	govt_complain_status = models.IntegerField(default=0) 
	user_complain_status = models.IntegerField(default=0) #0-not complete,1-complete
	user_complain_reason = models.TextField(blank=True)
	forum_visible = models.IntegerField(default=0)
	upvotes = models.IntegerField(default=0)
	rejection_reason = models.IntegerField(default=-1)    #1-this reason 2-this reason
	end_date = models.DateTimeField(null=True,blank=True)

class Complain_comments(models.Model):
	complain_id = models.IntegerField()
	comment_date = models.DateTimeField(default=datetime.now)
	comment_user = models.CharField(max_length=50)
	content = models.TextField()

class Complain_usercomments(models.Model):
	complain_id = models.IntegerField()
	comment_date = models.DateTimeField(default=datetime.now)
	comment_user = models.CharField(max_length=50)
	content = models.TextField()

class ComplainForm(ModelForm):
	class Meta:
		model = Complain
		fields = ['title','description','complain_image','complain_address','type_of_complain',"complain_place"]

class UserInfos(models.Model):
	user = models.OneToOneField(User)
	phone = models.CharField(max_length=20)
	address = models.TextField()
	locality = models.CharField(max_length=50)
	total_upvotes = models.IntegerField(default=0)
	ban_date = models.DateTimeField(null=True,blank=True)
	
class GovtUserInfo(models.Model):
	user = models.OneToOneField(User)
	phone = models.CharField(max_length=20)
	address = models.TextField()
	department =models.CharField(max_length=50)

class UserInfoForm(ModelForm):
	class Meta:
		model = User
		fields = ['username','first_name','last_name','email','password']

class LocalPlaces(models.Model):
	local_name = models.CharField(max_length=50)
	zipcode = models.CharField(max_length=6)

class Complain_type(models.Model):
	name = models.CharField(max_length=50)

class UserUpvoteStatus(models.Model):
	user_upvote = models.ForeignKey(User)
	upvote = models.IntegerField()


class Upvotenotification(models.Model):
	c_id = models.IntegerField()
	c_title = models.CharField(max_length=50)
	u_id = models.IntegerField()
	u_name = models.CharField(max_length=50)
	read = models.IntegerField(default=0)
	u_date = models.DateTimeField(default=datetime.now)

class Commentnotifications(models.Model):
	c_id = models.IntegerField()
	c_title = models.CharField(max_length=50)
	u_id = models.IntegerField()
	u_name = models.CharField(max_length=50)
	read = models.IntegerField(default=0)
	c_date = models.DateTimeField(default=datetime.now)
	comment = models.TextField()

class Statusnotifications(models.Model):
	c_id = models.IntegerField()
	c_title = models.CharField(max_length=50)
	status = models.IntegerField()
	read = models.IntegerField(default=0)	
	s_date = models.DateTimeField(default=datetime.now)
