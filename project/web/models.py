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
    
class GmailConnection(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    gmail_email = models.EmailField(blank=True)

    access_token = models.TextField()

    refresh_token = models.TextField()

    token_expiry = models.DateTimeField()

    connected = models.BooleanField(default=True)




class ATSResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    resume = models.FileField(upload_to="resumes/")
    job_description = models.TextField()

    resume_json = models.JSONField()
    jd_json = models.JSONField()

    ats_score = models.FloatField(default=0)

    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    recommended_skills = models.JSONField(default=list)

    strengths = models.JSONField(default=list)
    improvements = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.ats_score}"




class UserSkillProfile(models.Model):

    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name="skills"
    )

    technical_skills = models.JSONField(
        default=list,
        blank=True
    )

    tools = models.JSONField(
        default=list,
        blank=True
    )

    frameworks = models.JSONField(
        default=list,
        blank=True
    )

    databases = models.JSONField(
        default=list,
        blank=True
    )

    cloud_skills = models.JSONField(
        default=list,
        blank=True
    )

    soft_skills = models.JSONField(
        default=list,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    def __str__(self):
        return f"{self.profile.user.username} Skills"



class RecruiterJob(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True}) # Or extend via a profile type
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
     
    #zstore the req as list/json
    required_skills = models.JSONField(default=list, blank=True)
    
    redirect_url = models.URLField(blank=True, null=True, help_text="Link to external application form if applicable")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company}"
