from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)

    first_name = models.CharField(max_length=100)

    last_name  = models.CharField(max_length=100)

    email      = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True) 
    address = models.TextField(blank=True, null=True)


    city       = models.CharField(max_length=100)

    country    = models.CharField(max_length=100)

    def __str__(self):
        return self.first_name + "   " + self.last_name