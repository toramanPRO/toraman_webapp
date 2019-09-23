from django import forms
from django.contrib.auth.models import User

class PasswordResetForm(forms.Form):
    email = forms.EmailField()

class SetPasswordForm(forms.Form):
    pin = forms.IntegerField()
    password1 = forms.CharField(label="New Password", widget=forms.PasswordInput())
    password2 = forms.CharField(label="New Password (again)", widget=forms.PasswordInput())

class UserForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Password (again)", widget=forms.PasswordInput())
    class Meta():
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        