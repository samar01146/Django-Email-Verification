from django.contrib.auth.models import User
from .models import User
from django import forms

class UserForm(forms.ModelForm):
    email = forms.EmailField(max_length=200, help_text='Required')  
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="confirmpassword" , widget= forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username' , 'email' , 'mobile' , 'password' , 'password2']
        extra_kwargs = {'password1': {'write_only': True}}


def create(self, validated_data):
    print("🚀 ~ file: forms.py:14 ~ def", "def")
    user = User(
        email=validated_data['email'],
        username=validated_data['username']
    )
    user.set_password(validated_data['password'])
    print("🚀 ~ file: forms.py:20 ~ user", user)
    user.save()
    return user


class loginForm(forms.Form):
    username = forms.CharField(max_length= 100 , help_text ='Required')
    password = forms.CharField(max_length=100 , label="Password" , widget=forms.PasswordInput)
