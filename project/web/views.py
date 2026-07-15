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
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import auth
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import logout



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
# Forms
# ==========================================================

from .forms import (
    CreateUserForm,
    LoginForm,
    ProfileForm,
)


# ==========================================================
# Models
# ==========================================================

from .models import (
    ATSResult,
    GmailConnection,
    Profile,
    UserSkillProfile,
)


# ==========================================================
# Gmail Services
# ==========================================================

from .services.gmail_service import (
    exchange_code,
    get_google_flow,
    send_gmail,
)


# ==========================================================
# Resume & ATS Utilities
# ==========================================================

from .utils.ats_engine import calculate_ats
from .utils.groq_parser import (
    parse_job_description,
    parse_resume,
)
from .utils.pdf_parser import extract_resume_text


# ==========================================================
# Job Recommendation Engine
# ==========================================================

from web.recommendation.recc_engine import (
    get_recommendations,
    normalize_jobs,
    search_jobs,
)

# ==========================================================
# Chatbot
# ==========================================================


from web.AI_chatbot.chatbot import chatbot_response


def index(request):
        return render(request, "index.html")

def ai_email(request):
        return render(request, "ai_email.html")

def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    context= {"profile":profile}
    return render(request, "dashboard.html", context = context)


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
def disconnect_gmail(request):

    gmail = GmailConnection.objects.get(

        user=request.user

    )

    gmail.connected = False

    gmail.access_token = ""

    gmail.refresh_token = ""

    gmail.save()

    return redirect("settings")



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


#---------Recommendation------------

# 1. DASHBOARD VIEW: Shows all 20 raw jobs fetched from Adzuna
# def dashboard_all_jobs_view(request):
#     # For now, searching 'Python Developer'. 
#     raw_adzuna_jobs = search_jobs("Python Developer")
#     cleaned_adzuna_jobs = normalize_jobs(raw_adzuna_jobs)
    
#     context = {
#         'adzuna_jobs': cleaned_adzuna_jobs
#     }
#     return render(request, 'live_jobs.html', context)


# def dashboard_all_jobs_view(request):
#     query = request.GET.get('q', '').strip()
    
#     if not query:
#         search_query = "Python Developer"
#     else:
#         search_query = query
        
#     raw_adzuna_jobs = search_jobs(search_query)
#     cleaned_adzuna_jobs = normalize_jobs(raw_adzuna_jobs)

#     context = {
#         'adzuna_jobs': cleaned_adzuna_jobs,
#         'current_query': query
#     }
    
#     return render(request, 'dashboard.html', context)

# # 2. RECOMMENDATION VIEW: Shows your custom AI Top 10 matching jobs
# def recommendations_page_view(request):
#     # Dummy resume data for testing the algorithm match
#     sample_resume = {
#         "technical_skills": ["Python", "Django", "SQL", "Git"],
#         "tools": ["Docker"],
#         "frameworks": [],
#         "databases": ["PostgreSQL"],
#         "cloud_skills": ["AWS"],
#         "project_skills": [],
#         "soft_skills": ["Communication"],
#         "degrees": ["B.Tech Computer Science"],
#         "total_experience_years": 2,
#         "job_titles": ["Python Developer"]
#     }
    
#     # Gets the calculated top 10 recommended jobs via cosine similarity
#     recommended_jobs = get_recommendations(sample_resume)
    
#     context = {
#         'recommendations': recommended_jobs
#     }
#     return render(request, 'recomend_jobs.html', context)



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

@login_required
def edit_profile(request):

    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":

        form = ProfileForm(

            request.POST,

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

@login_required
def dashboard_all_jobs_view(request):
    query = request.GET.get('q', '').strip()
    
    # Check if a parsed resume exists to extract a smart default keyword
    latest_record = ATSResult.objects.filter(user=request.user).order_by('-created_at').first()
    
    if not query:
        # If there's a record, look inside your teammate's resume_json for their target job title
        if latest_record and latest_record.resume_json:
            # Safely gets target_role from json, falls back to "Python Developer" if missing
            extracted_role = latest_record.resume_json.get('personal_info', {}).get('target_role', '')
            search_query = extracted_role if extracted_role else "Python Developer"
        else:
            search_query = "Python Developer"
    else:
        search_query = query
        
    raw_adzuna_jobs = search_jobs(search_query)
    cleaned_adzuna_jobs = normalize_jobs(raw_adzuna_jobs)

    context = {
        'adzuna_jobs': cleaned_adzuna_jobs,
        'current_query': query
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

#----settings----

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

