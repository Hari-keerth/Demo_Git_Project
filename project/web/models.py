from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    age = models.IntegerField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    headline = models.CharField(max_length=255, blank=True)
    education = models.CharField(max_length=100, blank=True)
    experience_level = models.CharField(max_length=50, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
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
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    
    # NEW FIELDS:
    salary = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. ₹6,000,000 - ₹12,000,000 PA or $80k - $100k")
    experience_required = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. 2-4 Years or Entry Level")
     
    #zstore the req as list/json
    required_skills = models.JSONField(default=list, blank=True)
    
    redirect_url = models.URLField(blank=True, null=True, help_text="Link to external application form if applicable")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"
    

class Application(models.Model):
    STATUS_CHOICES = (
        ('Pending','Pending'),
        ('Shortlisted','Shortlisted'),
        ('Rejected','Rejected'),)
    job = models.ForeignKey(RecruiterJob, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    resume = models.FileField(upload_to='resumes/')
    cover_note = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    class Meta:
        unique_together = ('job', 'applicant')  # Prevents multiple application entries for the same job

    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"