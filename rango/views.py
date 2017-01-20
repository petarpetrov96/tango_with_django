from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

# Create your views here.

def index(request):
	context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
	return render(request,'rango/index.html',context=context_dict)

def about(request):
	context_dict = {'author': "Petar Petrov"}
	return render(request,'rango/about.html',context=context_dict)