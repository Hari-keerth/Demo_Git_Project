from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms.widgets import PasswordInput, TextInput
from django import forms
from .models import Profile


# -----------------------------
# Register User Form
# -----------------------------
class CreateUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "placeholder": "Enter Username",
            "class": "form-control"
        })

        self.fields["password1"].widget.attrs.update({
            "placeholder": "Enter Password",
            "class": "form-control"
        })

        self.fields["password2"].widget.attrs.update({
            "placeholder": "Confirm Password",
            "class": "form-control"
        })


# -----------------------------
# Register Profile Form
# (Used ONLY during registration)
# -----------------------------
class RegisterProfileForm(forms.ModelForm):

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
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter First Name"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Last Name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Email"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Phone Number"
            }),
            "age": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Age"
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter Address"
            }),
            "city": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter City"
            }),
            "country": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Country"
            }),
        }


# -----------------------------
# Login Form
# -----------------------------
class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=TextInput(attrs={
            "class": "email",
            "placeholder": "Enter Username",
            "autocomplete": "off",
        })
    )

    password = forms.CharField(
        widget=PasswordInput(attrs={
            "class": "password",
            "placeholder": "Enter Password",
            "autocomplete": "off",
        })
    )


# -----------------------------
# Full Profile Form
# (Used ONLY in profile page)
# -----------------------------
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

        # Keep all your existing widgets here
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