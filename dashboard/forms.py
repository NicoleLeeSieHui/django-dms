from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required') 
    class Meta:
        model = User
        fields = ['username','email','password1','password2']


class AdminRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required') 
    class Meta:
        model = User
        fields = ['username','email','password1','password2', 'is_staff', 'is_superuser']

class CheckBoxForm(forms.Form):
    my_checkbox = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'checkbox-class'}), label='Is Staff')

class UserPasswordForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['new_password1','new_password2']

class OwnPasswordForm(PasswordChangeForm):
    class Meta:
        model = User


        