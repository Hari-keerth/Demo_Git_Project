from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('ai_email/', views.ai_email, name='ai_email'),

    path('dashboard/', views.dashboard_all_jobs_view, name='dashboard'),

    path('login/', views.login, name='login'),

    path('register/', views.register, name='register'),

    path(
        'generate/',
        views.generate_documents,
        name='generate_documents'
    ),

    path(
        'download-cover-letter/',
        views.download_cover_letter,
        name='download_cover_letter'
    ),

    path(
        'download-email/',
        views.download_email,
        name='download_email'
    ),

    path(
        'send-application/',
        views.send_application,
        name='send_application'
    ),

    path(
        "api/send-email/",
        views.send_email_api,
        name="send_email_api"
    ),

    path(
        "download-email-pdf/",
        views.download_email_pdf,
        name="download_email_pdf"
    ),

    path(
        "download-cover-letter-pdf/",
        views.download_cover_letter_pdf,
        name="download_cover_letter_pdf"
    ),

    path(
        "profile/",
        views.profile,
        name="profile"
    ),

    path(
        "user-logout",
        views.user_logout,
        name="user-logout"
    ),

    #--gmail

    path(
        "google/login/",
        views.google_login,
        name="google_login"
    ),

    path(
        "google/callback/",
        views.google_callback,
        name="google_callback"
    ),

    path(

        "google/disconnect/",

        views.disconnect_gmail,

        name="disconnect_gmail"

    ),


    #--recommendation---

    # path(
    #     "dashboard_all_jobs_view/",
    #     views.dashboard_all_jobs_view,
    #     name="dashboard_all_jobs_view"
    # ),

    path(
        "recomend_jobs/",
        views.recommendations_page_view,
        name="recomend_jobs"
    ),


    #----ATS-----

    path(
        "resume-analyzer",
        views.resume_analyzer,
        name="resume-analyzer"),
    
    path(
        "calculate-ats/",
        views.calculate_ats_score,
        name="calculate_ats"
    ),

    # -------- Profile --------

    path(
        "profile/extract_skills/",
        views.extract_skills,
        name="extract_skills"
    ),

    path(
        "profile/edit_skills/",
        views.edit_skills,
        name="edit_skills"
    ),

    path(
        "profile/edit_profile/",
        views.edit_profile,
        name="edit_profile"
    ),

    #---chatbot---

    path("",views.chatbot,name="chatbot"),
    path('ask_ai/',views.ask_ai,name='ask_ai'),
    path('clear_chat/',views.clear_chat,name='clear_chat'),

    #recrutires jobs

    path(
        'jobs/post/',
        views.post_job_view, 
        name='post_job'),

    
    #--- Recruiter Dashboard ---
    path(
        'recruiter/dashboard/', 
        views.recruiter_dashboard_view, 
        name='recruiter_dashboard'
    ),

    #job Managementss
    path(
        'jobs/edit/<int:job_id>/',
        views.edit_job_view,
        name='edit_job'
    ),
   
   path(
       'jobs/delete/<int:job_id>/',
       views.delete_job_view,
       name='delete_job'
   ),

   
]