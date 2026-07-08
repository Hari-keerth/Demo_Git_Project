from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('ai_email/', views.ai_email, name='ai_email'),

    path('dashboard/', views.dashboard, name='dashboard'),

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
]