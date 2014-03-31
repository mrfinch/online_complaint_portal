from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from datetime import datetime
# Create your models here.

def content_file_name(instance,filename):
	print instance
	return '/'.join(["complaint_portal/images",instance.c_user.username,filename])
#make a list and pass it to template which will display it and store result in form of text
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
	days_to_solve = models.IntegerField(default=-1)
	upvotes = models.IntegerField(default=0)
	rejection_reason = models.IntegerField(default=-1)    #1-this reason 2-this reason
	user_complain_update = models.BooleanField(default=False)
	user_complain_reason = models.TextField(blank=True,null=True)

class ComplainForm(ModelForm):
	class Meta:
		model = Complain
		fields = ['title','description','complain_image','complain_address','type_of_complain',"complain_place"]
		#widgets = {'complain_date':HiddenInput(),}
'''
class UpdateComplainStatus(models.Model):
	c_id = models.OneToOneField(Complain)
	user_update = models.BooleanField()
	user_reason = models.TextField()
'''
class UpdateForm(ModelForm):
	class Meta:
		model = Complain
		fields = ['user_complain_update','user_complain_reason']
	
class UserInfo(models.Model):
	username = models.CharField(max_length=30)
	firstname = models.CharField(max_length=30)
	lastname = models.CharField(max_length=30)
	email = models.CharField(max_length=75)
	password = models.CharField(max_length=30)			
	phone = models.CharField(max_length=20)
	address = models.TextField()
	locality = models.CharField(max_length=50)  #locality table will have name of area corresponding value of locality selected
	total_upvotes = models.IntegerField(default=0)

class UserInfos(models.Model):
	username = models.CharField(max_length=30)
	firstname = models.CharField(max_length=30)
	lastname = models.CharField(max_length=30)
	email = models.CharField(max_length=75)
	password = models.CharField(max_length=30)			
	phone = models.CharField(max_length=20)
	address = models.TextField()
	locality = models.CharField(max_length=50)  #locality table will have name of area corresponding value of locality selected
	total_upvotes = models.IntegerField(default=0)

class UserInfoForm(ModelForm):
	class Meta:
		model = UserInfos
		fields = ['username','firstname','lastname','email','password','phone','address','locality']

class LocalPlaces(models.Model):
	local_name = models.CharField(max_length=50)
	zipcode = models.CharField(max_length=6)

class Complain_type(models.Model):
	name = models.CharField(max_length=50)

class UserUpvoteStatus(models.Model):
	user_upvote = models.ForeignKey(User)
	upvote = models.IntegerField()


#another table which will store complain's locality	 			 