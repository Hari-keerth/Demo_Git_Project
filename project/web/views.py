from django.shortcuts import render,redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import os
from .models import Profile

from .forms import ProfileForm
from .forms import CreateUserForm,LoginForm
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer
    )

from reportlab.lib.styles import (
        getSampleStyleSheet,
        ParagraphStyle
    )

from reportlab.lib.enums import TA_LEFT

from datetime import datetime

from django.core.mail import EmailMessage

from pypdf import PdfReader

from django.conf import settings

from .services.gmail_service import send_gmail
from .models import GmailConnection
from google_auth_oauthlib.flow import Flow
from .services.gmail_service import (
    get_google_flow,
    exchange_code
)
import tempfile
from googleapiclient.discovery import build

from web.recommendation.recc_engine import get_recommendations, normalize_jobs, search_jobs


import io
import json
import requests


def index(request):
        return render(request, "index.html")

def ai_email(request):
        return render(request, "ai_email.html")

def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    context= {"profile":profile}
    return render(request, "dashboard.html", context = context)


def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    context= {"profile":profile}
    gmail = GmailConnection.objects.filter(

        user=request.user,

        connected=True

    ).first()

    context={

        "gmail_connected":gmail is not None,

        "gmail_email":gmail.gmail_email if gmail else ""

    }
    return render(request, "profile.html",context = context)
    
@login_required
def disconnect_gmail(request):

    gmail = GmailConnection.objects.get(

        user=request.user

    )

    gmail.connected = False

    gmail.access_token = ""

    gmail.refresh_token = ""

    gmail.save()

    return redirect("profile")


def extract_resume_text(pdf_file):

        reader = PdfReader(pdf_file)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text


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
                "x-api-key": "sk-7IUtrMADNCiy2i5f_2Xqb8XW6VXPChN6QxPT9ybLITk"
            }

            response = requests.post(
                "http://localhost:7860/api/v1/run/a22d35d3-9187-4f90-be18-6ca1c9f5b8b6",
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
def register(request):
    if request.method == "POST":
        user_form = CreateUserForm(request.POST)
        profile_form = ProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # 1. Save the user first to generate their database ID
            new_user = user_form.save()
            
            # 2. Hold the profile in memory without writing to the database yet
            profile = profile_form.save(commit=False)
            
            # 3. Manually link the profile to the newly created user
            profile.user = new_user
            
            # 4. Now it is safe to save the profile to the database
            profile.save()
            
            return redirect('login')
    else:
        user_form = CreateUserForm()
        profile_form = ProfileForm()

    return render(request, 'register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })



#-- login a user

def login(request):
    form =LoginForm()
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username=request.POST.get('username')
            password=request.POST.get('password')
            user = authenticate(request , username=username , password=password)
            if user is not None:
                auth.login(request,user)
                messages.success(request ,'Logged in')
                return redirect('dashboard')
    context ={'form':form}

    return render (request,'login.html',context=context)



# user logout

def user_logout(request):
    auth.logout(request)
    messages.success(request ,'Logout Successful')
    return redirect("login")

#--gmail

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

    service = build(
        "gmail",
        "v1",
        credentials=credentials
    )

    profile = service.users().getProfile(
        userId="me"
    ).execute()

    GmailConnection.objects.update_or_create(

        user=request.user,

        defaults={

            "gmail_email": profile["emailAddress"],

            "access_token": credentials.token,

            "refresh_token": credentials.refresh_token,

            "token_expiry": credentials.expiry,

            "connected": True,

        }

    )

    return redirect("dashboard")


#---------Recommendation------------

# 1. DASHBOARD VIEW: Shows all 20 raw jobs fetched from Adzuna
def dashboard_all_jobs_view(request):
    # For now, searching 'Python Developer'. 
    raw_adzuna_jobs = search_jobs("Python Developer")
    cleaned_adzuna_jobs = normalize_jobs(raw_adzuna_jobs)
    
    context = {
        'adzuna_jobs': cleaned_adzuna_jobs
    }
    return render(request, 'live_jobs.html', context)

# 2. RECOMMENDATION VIEW: Shows your custom AI Top 10 matching jobs
def recommendations_page_view(request):
    # Dummy resume data for testing the algorithm match
    sample_resume = {
        "technical_skills": ["Python", "Django", "SQL", "Git"],
        "tools": ["Docker"],
        "frameworks": [],
        "databases": ["PostgreSQL"],
        "cloud_skills": ["AWS"],
        "project_skills": [],
        "soft_skills": ["Communication"],
        "degrees": ["B.Tech Computer Science"],
        "total_experience_years": 2,
        "job_titles": ["Python Developer"]
    }
    
    # Gets the calculated top 10 recommended jobs via cosine similarity
    recommended_jobs = get_recommendations(sample_resume)
    
    context = {
        'recommendations': recommended_jobs
    }
    return render(request, 'recomend_jobs.html', context)