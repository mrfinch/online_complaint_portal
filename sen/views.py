'''implemented index view
Authors:Saurabh
'''
from django.shortcuts import render
from django.http import HttpResponseRedirect

def home(request):
	'''redirecting to index view'''
	return HttpResponseRedirect("/complaint_portal/index") 
 
