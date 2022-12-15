from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.views import View
from .forms import UserForm , loginForm
from . models import User
from django.core.mail import send_mail
from verify_email.email_handler import send_verification_email
from django.http import HttpResponse  
from django.contrib.sites.shortcuts import get_current_site  
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.template.loader import render_to_string  
from app.token import account_activation_token  
from django.contrib.auth.models import User  
from django.core.mail import EmailMessage 
from django.contrib.auth import get_user_model
from django.db.models import Q


def home(request):
    return render(request, 'home.html')
 
class Register(View):  
    def get(self, request):
        form =  UserForm()
        return render(request, 'registration.html', {'form': form})
    def post(self, request):
        User = get_user_model()
        form = UserForm(request.POST)
        username = request.POST.get('username')
        if  request.POST.get('password') == request.POST.get('password2'):
            if not User.objects.filter(username=username):
                form = UserForm(request.POST)
                if form.is_valid():  
                    user = form.save(commit=False)  
                    user = User(
                        email=form.cleaned_data['email'],
                        username=form.cleaned_data['username'],
                        password = make_password(form.cleaned_data['password'])
                    )
                    user.is_active = False  
                    user.save()
                    current_site = get_current_site(request)  
                    mail_subject = 'Activation link has been sent to your email id'  
                    message = render_to_string('acc_active_email.html', {  
                        'user': user,  
                        'domain': current_site.domain,  
                        'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                        'token':account_activation_token.make_token(user),  
                    })
                    to_email = form.cleaned_data.get('email')  
                    email = EmailMessage(  
                                mail_subject, message, to=[to_email]  
                    )  
                    email.send()
                    return redirect('confirmlink')
                return redirect('login')
            else:
                messages.error(request , "User with this username already exist")
                return redirect('register')  
        else:
            messages.error(request , "Password does not match")
            print("password does not match")
        return redirect('register')
    
    
def activate(request, uidb64, token):
    User = get_user_model() 
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None  
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True  
        user.save()  
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')  
    else:  
        return HttpResponse('Activation link is invalid!')

class LoginView(View):
    def get(self , request):
        form = loginForm()
        return render(request , 'login.html', {'form':form})
    def post(self, request):
        User = get_user_model()
        username =  request.POST['username']
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            print("🚀 ~ file: views.py:93 ~ user", user)
            if user.is_active == True:
                form = loginForm(request.POST)
                if form.is_valid():
                    username = request.POST['username']
                    print("🚀 ~ file: views.py:96 ~ username", username)
                    password =  request.POST['password']
                    print("🚀 ~ file: views.py:98 ~ password", password)
                    user = authenticate(request, username=username , password=password)
                    print("🚀 ~ file: views.py:100 ~ user", user)
                    if user is not None:
                        form = login(request, user)
                        return redirect('home')
                    messages.error(request, "user does not exist")
                    return redirect('login')
                return render(request, 'login.html' , {'form':form})                
            else:
                to_email = User.objects.filter(username=username).values_list('email').first()[0]
                print("🚀 ~ file: views.py:125 ~ to_email", to_email)
                messages.error(request ,"username or password is incorrect please try again later")
                current_site = get_current_site(request)  
                mail_subject = 'Activation link has been sent to your email id'  
                message = render_to_string('acc_active_email.html', {  
                    'user': user,  
                    'domain': current_site.domain,  
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                    'token':account_activation_token.make_token(user),  
                })  
                username = request.POST['username']
                print("🚀 ~ file: views.py:124 ~ username", username)
                email = EmailMessage(  
                            mail_subject, message, to=[to_email]  
                )  
                email.send()
                messages.error(request, "you have not verify your email to login your account")
                return redirect('confirmlink')
        messages.error(request , "you have enter incorrect id or password")
        return redirect('login')

class Confirmlink(View):
    def get(self, request):
        return render(request, 'confirmlink.html')

def update_data(request , id):
    User = get_user_model()
    if request.method == 'POST':
        pi = User.objects.get(pk=id)
        fm = UserForm(request.POST , instance=pi)
        if fm.is_valid():
            fm.save()
        else:
            pi = User.objects.get(pk=id)
            fm = UserForm( instance=pi )
            return render(request , 'update.html', {'form': fm} )
        return render(request , 'update.html' )
    return render(request , 'update.html' )