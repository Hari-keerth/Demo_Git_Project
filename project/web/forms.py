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
          "first_name",
          "last_name",
          "email",
          "phone",
          "age",
          "address",
          "city",
          "country",
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Your First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Your Last Name',
                'rows': 3
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Your Email'
            }),
            'phone': forms.NumberInput(attrs={
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
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter City'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Country'
            }),
        }