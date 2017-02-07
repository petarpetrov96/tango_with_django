from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime

# Create your views here.

def index(request):
	request.session.set_test_cookie()
	category_list=Category.objects.order_by('-likes')[:5]
	pages_list=Page.objects.order_by('-views')[:5]
	context_dict = {'categories':category_list,'pages':pages_list}
	response=render(request,'rango/index.html',context=context_dict)
	visitor_cookie_handler(request,response)
	return response

def about(request):
	if request.session.test_cookie_worked():
		print("TEST COOKIE WORKED!")
		request.session.delete_test_cookie()
	context_dict = {'author': "Petar Petrov"}
	return render(request,'rango/about.html',context=context_dict)
	
def show_category(request, category_name_slug):
	context_dict={}
	try:
		category = Category.objects.get(slug=category_name_slug)
		pages = Page.objects.filter(category=category)
		context_dict['pages'] = pages
		context_dict['category'] = category
	except Category.DoesNotExist:
		context_dict['category'] = None
		context_dict['pages'] = None
	return render(request,'rango/category.html',context_dict)

@login_required
def add_category(request):
	form = CategoryForm()
	if request.method == "POST":
		form = CategoryForm(request.POST)
		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			print(form.errors)
	return render(request,'rango/add_category.html',{'form':form})

@login_required
def add_page(request,category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None
	
	form = PageForm()
	if request.method=="POST":
		form = PageForm(request.POST)
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
				return show_category(request,category_name_slug)
		else:
			print(form.error)
	context_dict={'form':form,'category':category}
	return render(request,'rango/add_page.html',context_dict)
	
def register(request):
	registered = False
	if request.method == "POST":
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)
			user.save()
			profile = profile_form.save(commit=False)
			profile.user=user
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			profile.save()
			registered = True
		else:
			print(user_form.errors,profile_form.errors)
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
	return render(request,'rango/register.html',{'user_form':user_form,'profile_form':profile_form,'registered':registered})

def user_login(request):
	if request.method=="POST":
		username=request.POST.get('username')
		password=request.POST.get('password')
		user=authenticate(username=username,password=password)
		if user:
			if user.is_active:
				login(request,user)
				return HttpResponseRedirect(reverse('index'))
			else:
				return HttpResponse('Your Rango account is disabled.')
		else:
			print("Invalid login details: {0}, {1}".format(username,password))
			return HttpResponse("Invalid login details supplied.")
	else:
		return render(request,'rango/login.html',{})

		
@login_required
def restricted(request):
	return render(request,'rango/restricted.html',{})

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

def visitor_cookie_handler(request,response):
	visits = int(request.COOKIES.get('visits','1'))
	last_visit_cookie = request.COOKIES.get('last_visit',str(datetime.now()))
	last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')
	if (datetime.now() - last_visit_time).days>0:
		visits = visits + 1
		response.set_cookie('last_visit',str(datetime.now()))
	else:
		visits = 1
		response.set_cookie('last_visit',last_visit_cookie)
	response.set_cookie('visits',visits)