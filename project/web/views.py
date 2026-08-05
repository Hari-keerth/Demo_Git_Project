# ==========================================================
# Python Standard Library
# ==========================================================

import io
import json
import os
import tempfile
from datetime import datetime

import requests


# ==========================================================
# Django Imports
# ==========================================================

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import auth
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


# ==========================================================
# Google Gmail API
# ==========================================================

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


# ==========================================================
# PDF Processing
# ==========================================================

from pypdf import PdfReader
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


# ==========================================================
# Local App: Forms
# ==========================================================

from .forms import (
    CreateUserForm,
    LoginForm,
    ProfileForm,
    RegisterProfileForm,
)

# ==========================================================
# Local App: Models
# ==========================================================

from .models import (
    ATSResult,
    Application,
    GmailConnection,
    Profile,
    RecruiterJob,
    UserSkillProfile,
)


# ==========================================================
# Local App: Gmail Services
# ==========================================================

from .services.gmail_service import (
    exchange_code,
    get_google_flow,
    send_gmail,
)


# ==========================================================
# Local App: Resume & ATS Utilities
# ==========================================================

from .utils.ats_engine import calculate_ats
from .utils.groq_parser import (
    parse_job_description,
    parse_resume,
)
from .utils.pdf_parser import extract_resume_text


# ==========================================================
# Local App: Resume Builder
# ==========================================================

from .resume_builder.resume_builder import generate_resume


# ==========================================================
# Local App: Job Recommendation Engine
# ==========================================================

from web.recommendation.recc_engine import (
    get_recommendations,
    normalize_jobs,
    search_jobs,
)


# ==========================================================
# Local App: Chatbot
# ==========================================================

from web.AI_chatbot.chatbot import chatbot_response


# ==========================================================
# Core / Static Pages
# ==========================================================

def index(request):
        return render(request, "index.html")


def ai_email(request):
        return render(request, "ai_email.html")


def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    context= {"profile":profile}
    return render(request, "dashboard.html", context = context)


# ==========================================================
# Authentication
# ==========================================================

def register(request):
    if request.method == "POST":
        user_form = CreateUserForm(request.POST)
        profile_form = RegisterProfileForm(request.POST)
        
        role = request.POST.get('role', 'candidate')
        
        #  TERMINAL DEBUG LOGS
        print("\n--- REGISTRATION ATTEMPT ---")
        print(f"Role Submitted: {role}")
        print(f"User Form Valid?: {user_form.is_valid()}")
        if not user_form.is_valid():
            print(f"User Form Errors: {user_form.errors}")
        print("-----------------------------\n")

        if role == 'recruiter':
            #  RECRUITER PATH: We only validate user_form!
            if user_form.is_valid():
                # 1. Save the new user and mark as Recruiter (staff status)
                new_user = user_form.save(commit=False)
                new_user.is_staff = True  
                new_user.save()
                
                # 2. Extract shared values directly from POST data
                first_name = request.POST.get('first_name', '')
                last_name = request.POST.get('last_name', '')
                email = request.POST.get('email', '')
                
                # 3. Create the Profile record directly using the model
                Profile.objects.create(
                    user=new_user,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone='',
                    age=None,
                    address='',
                    city='Not Specified',    # Fills required DB constraints securely
                    country='Not Specified'  # Fills required DB constraints securely
                )
                
                print("🎉 RECRUITER SAVED SUCCESSFULLY TO DATABASE!")
                messages.success(request, 'Recruiter registration successful! Please log in.')
                return redirect('login')
        else:
            #  CANDIDATE PATH: Both forms must be valid
            if user_form.is_valid() and profile_form.is_valid():
                new_user = user_form.save()
                profile = profile_form.save(commit=False)
                profile.user = new_user
                profile.save()
                
                print("🎉 CANDIDATE SAVED SUCCESSFULLY TO DATABASE!")
                messages.success(request, 'Registration successful! Please log in.')
                return redirect('login')
    else:
        user_form = CreateUserForm()
        profile_form = RegisterProfileForm() 

    return render(request, 'register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


#-- login a user


def login(request):
    form =LoginForm()
    if request.method == "POST":
        form = LoginForm(request, data=request.POST) # Keeps your exact form validation
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                auth_login(request, user)

                # Remember Me
                if request.POST.get("remember_me"):
                    # Keep user logged in for 30 days
                    request.session.set_expiry(60 * 60 * 24 * 30)
                else:
                    # Logout when browser closes
                    request.session.set_expiry(0)

                messages.success(request, 'Logged in')

                if user.is_staff:
                    return redirect('recruiter_dashboard')
                else:  
                    return redirect('dashboard') # Replace with your actual candidate URL name
                    
    context = {'form': form}
    return render(request, 'login.html', context=context)



# user logout


def user_logout(request):
    auth.logout(request)
    messages.success(request, 'Logout Successful')
    return redirect("login")

#--gmail


# ==========================================================
# Google Gmail Integration
# ==========================================================

def google_login(request):

    flow = get_google_flow()

    authorization_url, state = flow.authorization_url(

        access_type="offline",

        include_granted_scopes="true",

        prompt="consent"

    )

    request.session["google_state"] = state

    return redirect(authorization_url)


def google_callback(request):

    state = request.session.get("google_state")

    flow = get_google_flow(state)

    flow.fetch_token(
        authorization_response=request.build_absolute_uri()
    )

    credentials = flow.credentials

    userinfo = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={
            "Authorization": f"Bearer {credentials.token}"
        }
    ).json()

    email = userinfo["email"]

    GmailConnection.objects.update_or_create(

        user=request.user,

        defaults={

            "gmail_email": email,

            "access_token": credentials.token,

            "refresh_token": credentials.refresh_token,

            "token_expiry": credentials.expiry,

            "connected": True,

        }

    )

    return redirect("settings")


@login_required
def disconnect_gmail(request):

    gmail = GmailConnection.objects.get(

        user=request.user

    )

    gmail.connected = False

    gmail.access_token = ""

    gmail.refresh_token = ""

    gmail.save()

    return redirect("settings")


# ==========================================================
# Profile & Account Settings
# ==========================================================

@login_required
def profile(request):

    # Get or create user profile
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    # Get saved skills
    skills = UserSkillProfile.objects.filter(
        profile=profile
    ).first()

    context = {

        "profile": profile,

        "skills": skills

    }

    return render(
        request,
        "profile.html",
        context
    )


@login_required
def edit_profile(request):

    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        # Handle Delete Action
        if action == "delete":
            if profile.image:
                profile.image.delete(save=False)
                profile.image = None
                profile.save()
                messages.success(request, "Profile picture deleted.")
            return redirect("profile")

        form = ProfileForm(

            request.POST,

            request.FILES,

            instance=profile

        )

        if form.is_valid():

            form.save()

            messages.success(

                request,

                "Profile updated successfully."

            )

            return redirect("profile")

    else:

        form = ProfileForm(

            instance=profile

        )

    return render(

        request,

        "edit_profile.html",

        {

            "form": form

        }

    )

#-----chatbot---


@login_required
def settings_view(request):

    gmail = GmailConnection.objects.filter(

        user=request.user,

        connected=True

    ).first()

    context = {

        "gmail_connected": gmail is not None,

        "gmail_email":

            gmail.gmail_email if gmail else ""

    }

    return render(

        request,

        "settings.html",

        context

    )


@login_required
def change_password_view(request):

    if request.method == "POST":

        current = request.POST["current_password"]

        new = request.POST["new_password"]

        confirm = request.POST["confirm_password"]

        if not request.user.check_password(current):

            messages.error(
                request,
                "Current password is incorrect."
            )

            return redirect("settings")

        if new != confirm:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("settings")

        request.user.set_password(new)

        request.user.save()

        update_session_auth_hash(
            request,
            request.user
        )

        messages.success(
            request,
            "Password updated successfully."
        )

    return redirect("settings")


@login_required
def delete_account(request):

    if request.method == "POST":

        password = request.POST["password"]

        if not request.user.check_password(password):

            messages.error(
                request,
                "Incorrect password."
            )

            return redirect("settings")

        user = request.user

        logout(request)

        user.delete()

        messages.success(
            request,
            "Account deleted."
        )

        return redirect("login")

    return redirect("settings")


# ==========================================================
# Resume & ATS Analysis
# ==========================================================

def resume_analyzer(request):
        return render(request, "resume_analyzer.html")


def save_user_skills(user, resume_json):

    profile, _ = Profile.objects.get_or_create(
        user=user
    )

    UserSkillProfile.objects.update_or_create(

        profile=profile,

        defaults={

            "technical_skills":
                resume_json.get(
                    "technical_skills",
                    []
                ),

            "tools":
                resume_json.get(
                    "tools",
                    []
                ),

            "frameworks":
                resume_json.get(
                    "frameworks",
                    []
                ),

            "databases":
                resume_json.get(
                    "databases",
                    []
                ),

            "cloud_skills":
                resume_json.get(
                    "cloud_skills",
                    []
                ),

            "soft_skills":
                resume_json.get(
                    "soft_skills",
                    []
                )

        }

    )


@require_POST
@login_required
def calculate_ats_score(request):

    resume = request.FILES.get("resume")
    job_description = request.POST.get("job_description")


    # -----------------------------
    # Validation
    # -----------------------------

    if not resume:
        return JsonResponse({

            "success": False,

            "message": "Resume not uploaded."

        })


    if not job_description:

        return JsonResponse({

            "success": False,

            "message": "Job Description missing."

        })



    try:


        # -----------------------------
        # Step 1
        # Extract Resume Text
        # -----------------------------

        resume_text = extract_resume_text(
            resume
        )



        # -----------------------------
        # Step 2
        # Groq Resume Parsing
        # -----------------------------

        resume_json = parse_resume(
            resume_text
        )



        # -----------------------------
        # Step 3
        # Groq Job Description Parsing
        # -----------------------------

        jd_json = parse_job_description(
            job_description
        )



        # -----------------------------
        # Step 4
        # ATS Calculation
        # -----------------------------

        result = calculate_ats(

            resume_json,

            jd_json

        )



        # -----------------------------
        # Convert numpy values
        # -----------------------------

        def convert_numpy(obj):

            import numpy as np


            if isinstance(obj, np.generic):

                return obj.item()



            elif isinstance(obj, dict):

                return {

                    key: convert_numpy(value)

                    for key, value in obj.items()

                }



            elif isinstance(obj, list):

                return [

                    convert_numpy(item)

                    for item in obj

                ]


            return obj



        result = convert_numpy(
            result
        )



        # -----------------------------
        # Save User Skills
        # -----------------------------


        save_user_skills(
            request.user,
            resume_json
        )




        # -----------------------------
        # Save ATS Result
        # -----------------------------


        ATSResult.objects.create(


            user=request.user,


            resume=resume,


            job_description=job_description,


            resume_json=resume_json,


            jd_json=jd_json,


            ats_score=result.get(

                "ats_score",

                0

            ),



            matched_skills=result.get(

                "matched_skills",

                []

            ),



            missing_skills=result.get(

                "missing_skills",

                []

            ),



            recommended_skills=result.get(

                "recommended_skills",

                []

            ),



            strengths=result.get(

                "strengths",

                []

            ),



            improvements=result.get(

                "improvements",

                []

            )


        )




        # -----------------------------
        # Send Response to HTML
        # -----------------------------


        return JsonResponse({


            "success": True,


            "ats_score":

                result.get(

                    "ats_score",

                    0

                ),



            "matched_skills":

                result.get(

                    "matched_skills",

                    []

                ),



            "missing_skills":

                result.get(

                    "missing_skills",

                    []

                ),



            "recommended_skills":

                result.get(

                    "recommended_skills",

                    []

                ),



            "strengths":

                result.get(

                    "strengths",

                    []

                ),



            "improvements":

                result.get(

                    "improvements",

                    []

                )

        })



    except Exception as e:


        return JsonResponse({


            "success": False,


            "error": str(e)


        }, status=500)


@login_required
@require_POST
def extract_skills(request):

    resume = request.FILES.get("resume")

    if not resume:

        messages.error(
            request,
            "Please upload a resume."
        )

        return redirect("profile")

    try:

        resume_text = extract_resume_text(
            resume
        )

        resume_json = parse_resume(
            resume_text
        )

        save_user_skills(
            request.user,
            resume_json
        )

        messages.success(
            request,
            "Skills extracted successfully."
        )

    except Exception as e:

        messages.error(
            request,
            str(e)
        )

    return redirect("profile")


@login_required
def edit_skills(request):

    profile = Profile.objects.get(user=request.user)

    skill_profile, created = UserSkillProfile.objects.get_or_create(
        profile=profile
    )

    if request.method == "POST":

        skill_profile.technical_skills = [
            skill.strip()
            for skill in request.POST.get(
                "technical_skills",
                ""
            ).split(",")
            if skill.strip()
        ]

        skill_profile.frameworks = [
            skill.strip()
            for skill in request.POST.get(
                "frameworks",
                ""
            ).split(",")
            if skill.strip()
        ]

        skill_profile.tools = [
            skill.strip()
            for skill in request.POST.get(
                "tools",
                ""
            ).split(",")
            if skill.strip()
        ]

        skill_profile.databases = [
            skill.strip()
            for skill in request.POST.get(
                "databases",
                ""
            ).split(",")
            if skill.strip()
        ]

        skill_profile.cloud_skills = [
            skill.strip()
            for skill in request.POST.get(
                "cloud_skills",
                ""
            ).split(",")
            if skill.strip()
        ]

        skill_profile.soft_skills = [
            skill.strip()
            for skill in request.POST.get(
                "soft_skills",
                ""
            ).split(",")
            if skill.strip()
        ]

        skill_profile.save()

        messages.success(
            request,
            "Skills updated successfully."
        )

        return redirect("profile")

    context = {
        "skills": skill_profile
    }

    return render(
        request,
        "edit_skills.html",
        context
    )


# ==========================================================
# Resume Builder
# ==========================================================

def resume_builder(request):

    return render(
        request,
        "resume_builder.html"
    )


@require_POST
def generate_resume_view(request):

    try:

        data = json.loads(request.body)

        resume_html = generate_resume(data)

        return JsonResponse({

            "success": True,

            "resume_html": resume_html

        })

    except Exception as e:

        return JsonResponse({

            "success": False,

            "error": str(e)

        }, status=500)


# ==========================================================
# Document Generation & Email
# ==========================================================

@csrf_exempt
def generate_documents(request):

        if request.method != "POST":
            return JsonResponse(
                {"error": "POST request required"},
                status=400
            )

        try:

            job_description = request.POST.get(
                "job_description",
                ""
            )

            resume_file = request.FILES.get(
                "resume"
            )

            if not resume_file:

                return JsonResponse(
                    {
                        "error": "Resume PDF is required."
                    },
                    status=400
                )

            resume = extract_resume_text(
                resume_file
            )

            # ------ temp storage

            resume_file.seek(0)

            resume_path = default_storage.save(
                f"resumes/{resume_file.name}",
                resume_file
            )

            request.session["resume_path"] = resume_path

            # ------ temp storage
            input_text = f"""
    Job Description:
    {job_description}

    Resume:
    {resume}
    """

            headers = {
                "x-api-key": "sk-_uMdCD1VdeLpm-bA1elSRYCTJIc0j5cJgw_kVDx7TIo"
            }

            response = requests.post(
                "http://localhost:7860/api/v1/run/153927c3-a67d-4e19-bd9d-8921132aa9de",
                headers=headers,
                json={
                    "input_value": input_text,
                    "output_type": "chat",
                    "input_type": "chat"
                },
                timeout=60
            )

            response.raise_for_status()

            result = response.json()

            text = (
                result["outputs"][0]
                ["outputs"][0]
                ["results"]["message"]["text"]
            )

            try:

                parsed = json.loads(text)

                request.session["email_subject"] = parsed.get(
                    "email_subject",
                    ""
                )

                request.session["email_body"] = parsed.get(
                    "email_body",
                    ""
                )

                request.session["cover_letter"] = parsed.get(
                    "cover_letter",
                    ""
                )

                return JsonResponse(parsed)

            except json.JSONDecodeError:

                return JsonResponse({
                    "error": "Invalid JSON returned from Langflow",
                    "raw_output": text
                })

        except Exception as e:

            return JsonResponse({
                "error": str(e)
            }, status=500)


def download_cover_letter(request):

        cover_letter = request.session.get(
            "cover_letter",
            ""
        )

        if not cover_letter:
            return HttpResponse(
                "No cover letter available."
            )

        print("COVER LETTER:")
        print(repr(cover_letter))

        buffer = io.BytesIO()

        pdf = SimpleDocTemplate(
            buffer,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Title"],
            fontSize=18,
            spaceAfter=20
        )

        body_style = ParagraphStyle(
            "BodyStyle",
            parent=styles["Normal"],
            fontSize=11,
            leading=18,
            spaceAfter=12,
            alignment=TA_LEFT
        )

        content = []

        content.append(
            Paragraph(
                "Cover Letter",
                title_style
            )
        )

        today = datetime.now().strftime(
            "%d %B %Y"
        )

        content.append(
            Paragraph(
                today,
                body_style
            )
        )

        content.append(
            Spacer(1, 20)
        )

        paragraphs = [
            p.strip()
            for p in cover_letter.split("\n\n")
            if p.strip()
        ]

        for para in paragraphs:

            content.append(
                Paragraph(
                    para.replace(
                        "\n",
                        "<br/>"
                    ),
                    body_style
                )
            )

            content.append(
                Spacer(1, 12)
            )

        pdf.build(content)

        buffer.seek(0)

        response = HttpResponse(
            buffer,
            content_type="application/pdf"
        )

        response[
            "Content-Disposition"
        ] = (
            'attachment; filename="Cover_Letter.pdf"'
        )

        return response


def download_email(request):

        subject = request.session.get(
            "email_subject",
            ""
        )

        body = request.session.get(
            "email_body",
            ""
        )

        if not body:
            return HttpResponse(
                "No email available."
            )

        buffer = io.BytesIO()

        pdf = SimpleDocTemplate(
            buffer,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Title"],
            fontSize=18,
            spaceAfter=20
        )

        body_style = ParagraphStyle(
            "BodyStyle",
            parent=styles["Normal"],
            fontSize=11,
            leading=18,
            spaceAfter=12,
            alignment=TA_LEFT
        )

        content = []

        content.append(
            Paragraph(
                "Application Email",
                title_style
            )
        )

        content.append(
            Paragraph(
                f"<b>Subject:</b> {subject}",
                body_style
            )
        )

        content.append(
            Spacer(1, 20)
        )

        paragraphs = [
            p.strip()
            for p in body.split("\n\n")
            if p.strip()
        ]

        for para in paragraphs:

            content.append(
                Paragraph(
                    para.replace(
                        "\n",
                        "<br/>"
                    ),
                    body_style
                )
            )

            content.append(
                Spacer(1, 12)
            )

        pdf.build(content)

        buffer.seek(0)

        response = HttpResponse(
            buffer,
            content_type="application/pdf"
        )

        response[
            "Content-Disposition"
        ] = (
            'attachment; filename="Application_Email.pdf"'
        )

        return response


def create_cover_letter_pdf(cover_letter):

        buffer = io.BytesIO()

        pdf = SimpleDocTemplate(buffer)

        styles = getSampleStyleSheet()

        content = []

        content.append(
            Paragraph(
                "Cover Letter",
                styles["Title"]
            )
        )

        content.append(
            Spacer(1, 20)
        )

        paragraphs = [
            p.strip()
            for p in cover_letter.split("\n\n")
            if p.strip()
        ]

        for para in paragraphs:

            content.append(
                Paragraph(
                    para.replace(
                        "\n",
                        "<br/>"
                    ),
                    styles["Normal"]
                )
            )

            content.append(
                Spacer(1, 10)
            )

        pdf.build(content)

        buffer.seek(0)

        return buffer.getvalue()


@csrf_exempt
def send_application(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required"},
            status=400
        )

    try:

        data = json.loads(request.body)

        recruiter_email = data.get(
            "recruiter_email",
            ""
        ).strip()

        if not recruiter_email:

            return JsonResponse(
                {
                    "error":
                    "Recruiter email is required"
                },
                status=400
            )

        subject = data.get(
            "email_subject",
            ""
        )

        email_body = data.get(
            "email_body",
            ""
        )

        cover_letter = data.get(
            "cover_letter",
            ""
        )

        if not subject or not email_body:

            return JsonResponse(
                {
                    "error":
                    "Generate documents first"
                },
                status=400
            )

        # Get temporary resume path
        resume_path = request.session.get(
            "resume_path"
        )

        if not resume_path:

            return JsonResponse(
                {
                    "error":
                    "Resume not found. Please generate again."
                },
                status=400
            )

        # Create Cover Letter PDF
        cover_pdf = create_cover_letter_pdf(
            cover_letter
        )

        
        resume_full_path = os.path.join(
            settings.MEDIA_ROOT,
            resume_path
        )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_cover:

            temp_cover.write(cover_pdf)

            cover_path = temp_cover.name

        send_gmail(

            user=request.user,

            to_email=recruiter_email,

            subject=subject,

            body=email_body,

            attachments=[

                resume_full_path,

                cover_path

            ]

        )

        os.remove(cover_path)

        # Delete Temporary Resume
        resume_full_path = os.path.join(
            settings.MEDIA_ROOT,
            resume_path
        )

        if os.path.exists(
            resume_full_path
        ):
            os.remove(
                resume_full_path
            )

        # Remove session entry
        if "resume_path" in request.session:
            del request.session["resume_path"]

        return JsonResponse(
            {
                "message":
                f"Application sent successfully to {recruiter_email}"
            }
        )

    except Exception as e:

        return JsonResponse(
            {
                "error": str(e)
            },
            status=500
        )


@csrf_exempt
def send_email_api(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST required"},
            status=400
        )
    
    try:

        gmail = GmailConnection.objects.get(

            user=request.user,

            connected=True

        )

    except GmailConnection.DoesNotExist:

        return JsonResponse({

            "error":"Please connect Gmail first."

        }, status=400)

    try:

        data = json.loads(request.body)

        to_email = data.get("to")
        subject = data.get("subject")
        body = data.get("body")

        send_gmail(
            user=request.user,
            to_email=to_email,
            subject=subject,
            body=body
        )

        return JsonResponse({
            "status": "success"
        })

    except Exception as e:

        return JsonResponse({
            "error": str(e)
        }, status=500)


@csrf_exempt
def download_email_pdf(request):

        if request.method != "POST":
            return HttpResponse(
                "POST request required"
            )

        data = json.loads(request.body)

        subject = data.get(
            "email_subject",
            ""
        )

        body = data.get(
            "email_body",
            ""
        )

        buffer = io.BytesIO()

        pdf = SimpleDocTemplate(buffer)

        styles = getSampleStyleSheet()

        content = []

        content.append(
            Paragraph(
                "Application Email",
                styles["Title"]
            )
        )

        content.append(
            Paragraph(
                f"<b>Subject:</b> {subject}",
                styles["Normal"]
            )
        )

        content.append(
            Spacer(1, 20)
        )

        content.append(
            Paragraph(
                body.replace(
                    "\n",
                    "<br/>"
                ),
                styles["Normal"]
            )
        )

        pdf.build(content)

        buffer.seek(0)

        response = HttpResponse(
            buffer,
            content_type="application/pdf"
        )

        response[
            "Content-Disposition"
        ] = (
            'attachment; filename="Application_Email.pdf"'
        )

        return response


@csrf_exempt
def download_cover_letter_pdf(request):

        if request.method != "POST":
            return HttpResponse(
                "POST request required"
            )

        data = json.loads(request.body)

        cover_letter = data.get(
            "cover_letter",
            ""
        )

        buffer = io.BytesIO()

        pdf = SimpleDocTemplate(buffer)

        styles = getSampleStyleSheet()

        content = []

        content.append(
            Paragraph(
                "Cover Letter",
                styles["Title"]
            )
        )

        content.append(
            Spacer(1, 20)
        )

        content.append(
            Paragraph(
                cover_letter.replace(
                    "\n",
                    "<br/>"
                ),
                styles["Normal"]
            )
        )

        pdf.build(content)

        buffer.seek(0)

        response = HttpResponse(
            buffer,
            content_type="application/pdf"
        )

        response[
            "Content-Disposition"
        ] = (
            'attachment; filename="Cover_Letter.pdf"'
        )

        return response




# register a user


# ==========================================================
# AI Chatbot
# ==========================================================

def chatbot(request):
    response =''
    if request.method == 'POST':
        question= request.POST.get("question")
        response = chatbot_response(question,request)
    return render(
        request,
        "chatbot.html",
        {
            "response":response
        }
    )


def ask_ai(request):

    question = request.GET.get('question',"")

    answer = chatbot_response(question,request)

    return JsonResponse(
        {
            "response":answer
        }
    )


def clear_chat(request):
    request.session['conversation']=[]
    return JsonResponse(
        {
            'status':'success'
        }
    )


# ==========================================================
# Job Listings & Recommendations
# ==========================================================

@login_required
def dashboard_all_jobs_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # SECURITY FIX: Stop recruiters from seeing the candidate view!
    if request.user.is_staff:
        return redirect('recruiter_dashboard')

    # -------------------------------------------------------------
    # 1. CALCULATE PROFILE COMPLETION & JOBS APPLIED METRICS
    # -------------------------------------------------------------
    user = request.user
    total_fields = 4
    completed_fields = 0

    if user.first_name and user.last_name:
        completed_fields += 1
    if user.email:
        completed_fields += 1
    if getattr(profile, 'bio', None) or getattr(profile, 'phone', None) or getattr(profile, 'headline', None):
        completed_fields += 1
    if getattr(profile, 'resume', None) or getattr(profile, 'skills', None):
        completed_fields += 1

    profile_completion = int((completed_fields / total_fields) * 100)

    # Fetch total jobs applied by this candidate
    applied_count = Application.objects.filter(applicant=user).count()

    # -------------------------------------------------------------
    # 2. JOB SEARCH & QUERY LOGIC
    # -------------------------------------------------------------
    query = request.GET.get('q', '').strip()
    location_query = request.GET.get('location', '').strip()

    search_query = query if query else "Python Developer"

    # db recruiters job
    db_jobs = RecruiterJob.objects.all().order_by('-created_at')

    if query:
        db_jobs = db_jobs.filter(
            Q(title__icontains=query) | 
            Q(company_name__icontains=query) |
            Q(description__icontains=query)
        )
    
    if location_query:
        db_jobs = db_jobs.filter(
            Q(location__icontains=location_query)
        )

    # Limit results to 5 if no search filter was applied
    if not query and not location_query:
        db_jobs = db_jobs[:5]

    local_recruiter_jobs = []
    for r_job in db_jobs:
        if isinstance(r_job.required_skills, list):
            skills_list = r_job.required_skills
        elif isinstance(r_job.required_skills, str):
            skills_list = [s.strip() for s in r_job.required_skills.split(',') if s.strip()]
        else:
            skills_list = []

        local_recruiter_jobs.append({
            'title': r_job.title,
            'company': f"{r_job.company_name} (Featured)",
            'location': r_job.location,
            'description': r_job.description,
            'salary': r_job.salary,
            'experience_required': r_job.experience_required,
            'redirect_url': f"/jobs/apply/{r_job.id}/",
            'contract_time': "Full Time",
            'skills': skills_list,
            'is_local': True,
        })

    try:
        raw_adzuna_jobs = search_jobs(search_query, location=location_query) if location_query else search_jobs(search_query)
        cleaned_adzuna_jobs = normalize_jobs(raw_adzuna_jobs)
    except Exception as e:
        print(f"API Error: {e}")
        cleaned_adzuna_jobs = []
    
    # Combine listings
    combined_job_listings = local_recruiter_jobs + cleaned_adzuna_jobs

    # -------------------------------------------------------------
    # 3. PASS TO CONTEXT
    # -------------------------------------------------------------
    context = {
        'profile': profile,
        'adzuna_jobs': combined_job_listings,
        'current_query': query,
        'current_location': location_query,
        'applied_count': applied_count,              
        'profile_completion': profile_completion,  
    }
    return render(request, 'dashboard.html', context)


# 2. RECOMMENDATION VIEW: Dynamic Live Matching based on teammate's model database data


@login_required
def recommendations_page_view(request):
    # 1. 🟢 Grab the latest ATSResult record to verify they have uploaded a resume
    latest_record = ATSResult.objects.filter(user=request.user).order_by('-created_at').first()
    
    # 2. 🟢 Pull the structured UserSkillProfile linked to this user's profile
    user_profile = getattr(request.user, 'profile', None)
    skill_profile = getattr(user_profile, 'skills', None) if user_profile else None
    
    recommended_jobs = []
    
    # We only run the engine if they have a saved skill profile
    if skill_profile:
        # Get target role from ATSResult if available, fallback to "Developer"
        target_role = "Developer"
        if latest_record and latest_record.resume_json:
            target_role = latest_record.resume_json.get("personal_info", {}).get("target_role", "Developer")

        # 3. 🟢 Build the profile using the exact fields from UserSkillProfile!
        user_profile_data = {
            "technical_skills": skill_profile.technical_skills,  # From UserSkillProfile
            "tools": skill_profile.tools,                        # From UserSkillProfile
            "frameworks": skill_profile.frameworks,              # From UserSkillProfile
            "databases": skill_profile.databases,                # From UserSkillProfile
            "cloud_skills": skill_profile.cloud_skills,          # From UserSkillProfile
            "soft_skills": skill_profile.soft_skills,            # From UserSkillProfile
            "project_skills": [],                                # Safe empty fallback
            "degrees": [],                                       # Safe empty fallback
            "total_experience_years": 0,                         # Safe empty fallback
            "job_titles": [target_role]
        }
        
        # 4. 🟢 Run your recommendation algorithm with the clean database profile
        recommended_jobs = get_recommendations(user_profile_data)
        
    context = {
        'recommendations': recommended_jobs,
        # If they have a skill profile, we consider their record active
        'has_record': skill_profile is not None  
    }
    return render(request, 'recomend_jobs.html', context)


# ==========================================================
# Recruiter Job Management
# ==========================================================

@login_required
def post_job_view(request):
    # Only allow recruiters (is_staff = True) to post jobs
    if not request.user.is_staff:
        messages.error(request, "Access denied. Only recruiters can post jobs.")
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        company = request.POST.get('company_name')
        location = request.POST.get('location')
        description = request.POST.get('description')
        redirect_url = request.POST.get('redirect_url') 
        salary = request.POST.get('salary', '')
        experience_required = request.POST.get('experience_required', '') or None
        
        # Get raw skills input, split by comma, and clean up empty spaces
        raw_skills = request.POST.get('required_skills', '')
        required_skills_list = [skill.strip() for skill in raw_skills.split(',') if skill.strip()]

        # Save to your RecruiterJob model
        RecruiterJob.objects.create(
            recruiter=request.user,
            title=title,
            company_name=company,
            location=location,
            salary=salary,                         
            experience_required=experience_required,
            description=description,
            required_skills=required_skills_list,  # Saves beautifully as a JSON list
            redirect_url=redirect_url
        )

        messages.success(request, "Job opportunity published successfully! 🚀")
        return redirect('recruiter_dashboard')

    return render(request, 'post_job.html')


@login_required
def recruiter_dashboard_view(request):
    # Security Check: Redirect non-recruiters back to candidate dashboard
    if not request.user.is_staff:
        return redirect('dashboard')
        
    # Fetch all jobs posted by this specific recruiter[cite: 1]
    my_jobs = RecruiterJob.objects.filter(recruiter=request.user).order_by('-created_at')
    
    context = {
        'my_jobs': my_jobs,
        'total_jobs': my_jobs.count()
    }
    return render(request, 'recruiter_dashboard.html', context)


@login_required
def edit_job_view(request, job_id):
    # Fetch the specific job or throw a 404
    job = get_object_or_404(RecruiterJob, id=job_id)
    
    # Security: Double check that this recruiter owns the job post[cite: 1]
    if job.recruiter != request.user:
        messages.error(request, "You do not have permission to edit this job.")
        return redirect('recruiter_dashboard')

    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.company = request.POST.get('company')
        job.location = request.POST.get('location')
        job.description = request.POST.get('description')
        job.redirect_url = request.POST.get('redirect_url') or None
        
        raw_skills = request.POST.get('required_skills', '')
        job.required_skills = [skill.strip() for skill in raw_skills.split(',') if skill.strip()]
        
        job.save()
        messages.success(request, "Job posting updated successfully! ")
        return redirect('recruiter_dashboard')

    # Join the skills array back into a comma-separated string for the text input form
    skills_string = ", ".join(job.required_skills) if job.required_skills else ""
    
    return render(request, 'edit_job.html', {'job': job, 'skills_string': skills_string})


@login_required
def delete_job_view(request, job_id):
    job = get_object_or_404(RecruiterJob, id=job_id)
    
    # Security: Ensure ownership[cite: 1]
    if job.recruiter != request.user:
        messages.error(request, "You do not have permission to delete this job.")
        return redirect('recruiter_dashboard')
        
    job.delete()
    messages.success(request, "Job posted Deleted.")
    return redirect('recruiter_dashboard')
#----settings----


# ==========================================================
# Job Applications
# ==========================================================

@login_required
def apply_job_view(request, job_id):
    job = get_object_or_404(RecruiterJob, id=job_id)

    # Prevent Duplicate Applications
    existing_application = Application.objects.filter(job=job, applicant=request.user).exists()
    if existing_application:
        messages.warning(request, f"You have already applied for '{job.title}'.")
        return redirect('dashboard')

    # Get user profile & latest ATS result
    user_profile = getattr(request.user, 'profile', None)
    latest_ats_result = ATSResult.objects.filter(user=request.user).order_by('-created_at').first()

    latest_resume = None
    if latest_ats_result and latest_ats_result.resume:
        latest_resume = latest_ats_result.resume
    elif user_profile and hasattr(user_profile, 'resume') and user_profile.resume:
        latest_resume = user_profile.resume

    if request.method == 'POST':
        uploaded_resume = request.FILES.get('resume')
        cover_note = request.POST.get('cover_note', '')
        use_existing = request.POST.get('use_existing_resume') == 'true'

        application = Application(
            job=job,
            applicant=request.user,
            cover_note=cover_note
        )

        if uploaded_resume:
            application.resume = uploaded_resume
            application.save()
        elif use_existing and latest_resume:
            try:
                latest_resume.open()
                application.resume.save(
                    latest_resume.name.split('/')[-1],
                    ContentFile(latest_resume.read()),
                    save=True
                )
            except FileNotFoundError:
                messages.error(request, "Your saved resume file could not be found. Please upload a new resume.")
                return render(request, 'apply_job.html', {'job': job, 'latest_resume': None})
        else:
            messages.error(request, "Please upload or attach a resume to submit your application.")
            return render(request, 'apply_job.html', {'job': job, 'latest_resume': latest_resume})

        messages.success(request, f"Application for '{job.title}' submitted successfully!")
        return redirect('dashboard')

    return render(request, 'apply_job.html', {'job': job, 'latest_resume': latest_resume})

# views.py


@login_required
def job_applications_view(request, job_id):
    # Security: Ensure only staff/recruiters can access
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    job = get_object_or_404(RecruiterJob, id=job_id)

    # Security: Ensure recruiter owns this job post
    if job.recruiter != request.user:
        messages.error(request, "You do not have permission to view applications for this job.")
        return redirect('recruiter_dashboard')

    # Fetch all applications for this job
    applications = Application.objects.filter(job=job).select_related('applicant', 'applicant__profile').order_by('-applied_at')

    context = {
        'job': job,
        'applications': applications,
        'total_applications': applications.count()
    }
    return render(request, 'job_applications.html', context)


@login_required
def applied_jobs_view(request):
    # Fetch all job applications for the logged-in candidate
    applications = Application.objects.filter(applicant=request.user).order_by('-applied_at')
    
    context = {
        'applications': applications,
        'active_page': 'applied_jobs'
    }
    return render(request, 'applied_jobs.html', context)


#---------mock_test----

import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

# =====================================================================
# CONFIG — swap these two flow IDs for your actual Langflow flow IDs
# =====================================================================

LANGFLOW_BASE_URL = "http://localhost:7860/api/v1/run"
LANGFLOW_QUESTION_FLOW_ID = "472e1392-4d71-4175-8ba5-ef833f0e9eae"
LANGFLOW_EVALUATE_FLOW_ID = "74e5a1a4-4c5c-4e74-af3d-b25075014bb3"

# Move this to an environment variable / Django setting before deploying —
# do not leave API keys hardcoded in source.
LANGFLOW_API_KEY = "sk-vpYUZw85P4Y8BefM1lsCpfosfjXWOeH70zxjK4zb6-g"


class LangflowError(Exception):
    """
    Raised when Langflow itself returns a non-2xx response. Carries the
    actual response body, since Langflow puts the real failure reason
    there (a bad/missing API key on one of the flow's components, a
    misconfigured model, a Structured Output schema mismatch, etc.) --
    response.raise_for_status() alone only gives you a generic
    "500 Server Error ... for url: ..." with none of that detail.
    """
 
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Langflow returned {status_code}: {detail}")
 
 
def call_langflow(flow_id, input_text, timeout=60):
    """
    Shared helper for calling a Langflow flow and pulling the text
    response out of its output shape. Raises LangflowError (with the
    real error body attached) on a non-2xx response, or a
    requests.RequestException on network-level failures (timeout,
    connection refused, etc). Callers are expected to catch both and
    convert to a JsonResponse.
    """
 
    response = requests.post(
        f"{LANGFLOW_BASE_URL}/{flow_id}",
        headers={"x-api-key": LANGFLOW_API_KEY},
        json={
            "input_value": input_text,
            "output_type": "chat",
            "input_type": "chat",
        },
        timeout=timeout,
    )
 
    if not response.ok:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        raise LangflowError(response.status_code, detail)
 
    result = response.json()
 
    return result["outputs"][0]["outputs"][0]["results"]["message"]["text"]
 
 
# =====================================================================
# PAGE
# =====================================================================
 
def mock_interview_page(request):
    return render(request, "mock_interview.html")
 
 
# =====================================================================
# QUESTION GENERATION
# =====================================================================
 
@require_POST
def generate_interview_question(request):
 
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON body."}, status=400)
 
    role = (data.get("role") or "").strip()
    difficulty = (data.get("difficulty") or "").strip()
    total_questions = data.get("total_questions")
    asked_questions = data.get("asked_questions", [])
 
    if not role:
        return JsonResponse({"success": False, "error": "Job role is required."}, status=400)
 
    if not difficulty:
        return JsonResponse({"success": False, "error": "Difficulty is required."}, status=400)
 
    # ---- server-side cap enforcement (fixes the overshoot bug for real) ----
    try:
        total_questions = int(total_questions)
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "total_questions is required."}, status=400)
 
    if len(asked_questions) >= total_questions:
        return JsonResponse({
            "success": False,
            "error": "Question limit reached for this interview.",
        }, status=400)
 
    # ---- build the prompt input ----
    if asked_questions:
        asked_block = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(asked_questions))
    else:
        asked_block = "(none yet -- this is the first question)"
 
    input_text = (
        f"Role: {role}\n"
        f"Difficulty: {difficulty}\n"
        f"Already Asked:\n{asked_block}\n"
    )
 
    try:
        question = call_langflow(LANGFLOW_QUESTION_FLOW_ID, input_text).strip()
    except requests.Timeout:
        return JsonResponse({"success": False, "error": "Question generation timed out."}, status=504)
    except LangflowError as e:
        # e.detail is Langflow's actual error body -- check the Django
        # console/logs (or this response, during debugging) for the real
        # component-level failure reason instead of a generic 500.
        return JsonResponse({
            "success": False,
            "error": f"Langflow error ({e.status_code})",
            "detail": e.detail,
        }, status=502)
    except requests.RequestException as e:
        return JsonResponse({"success": False, "error": str(e)}, status=502)
    except (KeyError, IndexError):
        return JsonResponse({"success": False, "error": "Unexpected response from Langflow."}, status=502)
 
    if not question:
        return JsonResponse({"success": False, "error": "Empty question returned."}, status=502)
 
    return JsonResponse({"success": True, "question": question})
 
 
# =====================================================================
# EVALUATION
# =====================================================================
 
@require_POST
def evaluate_interview(request):
 
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON body."}, status=400)
 
    role = (data.get("role") or "").strip()
    interview_data = data.get("interview_data", [])
 
    if not role:
        return JsonResponse({"success": False, "error": "Job role is required."}, status=400)
 
    if not interview_data:
        return JsonResponse({"success": False, "error": "No interview answers to evaluate."}, status=400)
 
    qa_block = "\n\n".join(
        f"Q{i + 1}: {item.get('question', '')}\n"
        f"A{i + 1}: {item.get('answer', '') or '(skipped -- no answer given)'}"
        for i, item in enumerate(interview_data)
    )
 
    input_text = (
        f"Role: {role}\n\n"
        f"Interview transcript:\n{qa_block}\n"
    )
 
    try:
        raw_text = call_langflow(LANGFLOW_EVALUATE_FLOW_ID, input_text, timeout=90)
    except requests.Timeout:
        return JsonResponse({"success": False, "error": "Evaluation timed out."}, status=504)
    except LangflowError as e:
        return JsonResponse({
            "success": False,
            "error": f"Langflow error ({e.status_code})",
            "detail": e.detail,
        }, status=502)
    except requests.RequestException as e:
        return JsonResponse({"success": False, "error": str(e)}, status=502)
    except (KeyError, IndexError):
        return JsonResponse({"success": False, "error": "Unexpected response from Langflow."}, status=502)
 
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON returned from Langflow.",
            "raw_output": raw_text,
        }, status=502)
 
    # Defensive: json.loads() succeeds on ANY valid JSON, not just objects --
    # a bare number, string, or list all parse fine but have no .get(). If the
    # flow ever returns something that isn't a JSON object (e.g. just "1"),
    # fail loudly with the raw output visible instead of silently building a
    # near-empty report.
    if not isinstance(parsed, dict):
        return JsonResponse({
            "success": False,
            "error": "Langflow did not return a JSON object as expected.",
            "raw_output": raw_text,
        }, status=502)
 
    # normalize so renderReport() in interview.js always has what it expects.
    # "success": True is required here -- evaluateInterview() in interview.js
    # checks `!response.ok || !data.success` before rendering the report, so
    # a response missing this field gets treated as a failure even when the
    # evaluation itself worked fine.
    return JsonResponse({
        "success": True,
        "overall_score": parsed.get("overall_score", parsed.get("score", 0)),
        "strengths": parsed.get("strengths", []),
        "improvements": parsed.get("improvements", []),
        "reviews": parsed.get("reviews", []),
        "study_plan": parsed.get("study_plan", []),
    })
#-------------------------------------------------------------------------------------------------


from pathlib import Path
import tempfile
import time

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .ai_agent.runner import run_agent


def ai_agent_page(request):
    """
    Render the AI Agent page.
    """
    return render(request, "ai_agent.html")


@require_POST
def run_ai_agent(request):
    """
    Receives:
        - Resume PDF
        - Job Description
        - Recruiter Email

    Executes the AI Agent and returns the generated JSON.
    """

    try:
        resume = request.FILES.get("resume")
        job_description = request.POST.get("job_description", "").strip()
        recruiter_email = request.POST.get("recruiter_email", "").strip()

        if not resume:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Resume PDF is required.",
                },
                status=400,
            )

        if not job_description:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Job description is required.",
                },
                status=400,
            )

        start_time = time.perf_counter()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            for chunk in resume.chunks():
                temp_pdf.write(chunk)

            resume_path = Path(temp_pdf.name)

        result = run_agent(
            resume_path=resume_path,
            job_description=job_description,
            recruiter_email=recruiter_email,
        )

        execution_time = round(time.perf_counter() - start_time, 2)

        return JsonResponse(
            {
                "success": True,
                "execution_time": execution_time,
                **result,
            }
        )

    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "error": str(e),
            },
            status=500,
        )