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
            "headline",
            "experience_level",
            "years_of_experience",
            "education",
            "city",
            "country",
            "address",
            "bio",
            "profile_picture",
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Email Address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Phone Number'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Age'
            }),
            'headline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Senior Software Engineer | Python & Django'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_experience_level'
            }, choices=[
                ('fresher', 'Fresher / Entry Level'),
                ('experienced', 'Experienced Professional'),
            ]),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 3',
                'id': 'id_years_of_experience'
            }),
            'education': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('', 'Select Highest Education'),
                ('high_school', 'High School Diploma'),
                ('bachelors', "Bachelor's Degree"),
                ('masters', "Master's Degree"),
                ('phd', 'Doctorate / PhD'),
                ('diploma', 'Diploma / Certification'),
                ('other', 'Other'),
            ]),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter City'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Country'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Street Address',
                'rows': 3
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write a brief summary of your background, career goals, and experience...',
                'rows': 4
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*',
            }),
        }