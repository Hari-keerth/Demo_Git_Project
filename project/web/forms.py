from django.contrib.auth.forms import UserCreationForm , AuthenticationForm
from django.contrib.auth.models import User
from django.forms.widgets import PasswordInput,TextInput

from django import forms
from .models import Profile
# register/create a user

class CreateUserForm(UserCreationForm):

    class Meta:

        model = User
        fields = ['username', 'password1', 'password2']


# login a user
class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=TextInput(
            attrs={
                "class": "email",
                "placeholder": "Enter Username",
                "autocomplete": "off",
            }
        )
    )

    password = forms.CharField(
        widget=PasswordInput(
            attrs={
                "class": "password",
                "placeholder": "Enter Password",
                "autocomplete": "off",
            }
        )
    )

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [
            'phone',
            'address',
            'age',
        ]

        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Phone Number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Address',
                'rows': 3
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Age'
            }),
        }