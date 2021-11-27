from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from booking.forms import NewUserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm


def register_request(request):
    if request.method == "POST":
       
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            redirect_url = request.GET.get('next', None)
            if redirect_url:
                return HttpResponseRedirect(redirect_url)
            else:
                return render(request, "index.html", {})
    
        messages.error(request, "Unsuccessful registration. Invalid information.")
        
    form = NewUserForm()
    return render(request, "register.html", context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                redirect_url = request.GET.get('next', None)
                if redirect_url:
                    return HttpResponseRedirect(redirect_url)
                else:
                    return render(request, "index.html", {})
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form": form})

def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return render(request, "index.html", {})