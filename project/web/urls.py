from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from . import password_views

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

   
    #----settings-----

    path(
        "settings/",
        views.settings_view,
        name="settings"
    ),

    path(
        "change-password/",
        views.change_password_view,
        name="change_password"
    ),

    path(
        "delete-account/",
        views.delete_account,
        name="delete_account"
    ),

    #----resume_builder-----
    
    path(
        "resume_builder/",
        views.resume_builder,
        name="resume_builder",
    ),

    path(
        "generate-resume/",
        views.generate_resume_view,
        name="generate_resume",
    ),

    #----forgot_password------

    path(
        "forgot-password/",
        password_views.forgot_password,
        name="forgot_password",
    ),

    path(
        "verify-otp/",
        password_views.verify_otp,
        name="verify_otp",
    ),

    path(
        "reset-password/",
        password_views.reset_password,
        name="reset_password",
    ),

    path(
        "resend-otp/",
        password_views.resend_otp,
        name="resend_otp",
    ),

    #--job----

    path(
        'jobs/apply/<int:job_id>/', 
        views.apply_job_view, 
        name='apply_job'
    ),
    
  
    path(
        'recruiter/job/<int:job_id>/applications/', 
        views.job_applications_view, 
        name='job_applications'
    ),

    
    path(
        'dashboard/', 
        views.dashboard_all_jobs_view, 
        name='dashboard'
    ),

    path(
        'applied-jobs/', 
        views.applied_jobs_view, 
        name='applied_jobs'
    ),

    #---------------
    #---------------------------------sravan------------------------------------------------

    # -----------------------------
    # Mock Interview Page
    # -----------------------------
    # Page
    path("interview/", views.mock_interview_page, name="mock_interview"),

    # AI endpoints
    path("interview/question/", views.generate_interview_question, name="interview_question"),
    path("interview/evaluate/", views.evaluate_interview, name="interview_evaluate"),


    path(
        "ai_agent/",
        views.ai_agent_page,
        name="ai_agent",
    ),

    path(
        "ai-agent/run/",
        views.run_ai_agent,
        name="run_ai_agent",
    ),
    
    path(
        'recruiter/company-profile/', 
        views.company_profile_view, 
        name='company_profile'

    ),

    path(
        'recruiter/applicants/', 
        views.recruiter_applicants_view, 
        name='recruiter_applicants'

    ),

    path(
        'recruiter/applicant/<int:app_id>/update-status/', 
        views.update_applicant_status_view, 
        name='update_applicant_status'

    ),

    #---resume---

    path(
            "resume-analyzer/",
            views.resume_analyzer,
            name="resume_analyzer",
        ),

    path(
        "calculate-ats/",
        views.calculate_ats,
        name="calculate_ats",
    ),

    
]

