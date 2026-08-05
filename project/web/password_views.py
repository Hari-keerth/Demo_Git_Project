import secrets,random

from datetime import timedelta

from django.conf import settings

from django.contrib import messages

from django.contrib.auth.models import User

from .models import Profile

from django.core.mail import send_mail

from django.shortcuts import render, redirect

from django.utils import timezone

from django.contrib.auth.hashers import make_password

from django.contrib.auth.hashers import check_password

from django.utils.dateparse import parse_datetime

from django.contrib.auth.password_validation import validate_password

from django.core.exceptions import ValidationError

def clear_reset_session(request):
    """
    Remove only password-reset related session data.
    Keeps the user's normal session intact.
    """
    keys = [
        "reset_username",
        "reset_email",
        "reset_otp",
        "otp_expiry",
        "otp_attempts",
        "otp_verified",
    ]

    for key in keys:
        request.session.pop(key, None)

def forgot_password(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()

        email = request.POST.get("email", "").strip().lower()

        if not username or not email:

            messages.error(
                request,
                "Please enter username and email."
            )

            return render(
                request,
                "password/forgot_password.html"
            )

        try:

            profile = Profile.objects.get(
                user__username=username,
                email=email
            )

            user = profile.user

        except Profile.DoesNotExist:

            messages.error(

                request,

                "Username and email do not match."

            )

            return render(

                request,

                "password/forgot_password.html"

            )

        otp = f"{secrets.randbelow(900000) + 100000}"

        request.session["reset_username"] = username

        request.session["reset_email"] = email

        request.session["reset_otp"] = make_password(otp)

        request.session["otp_expiry"] = (

            timezone.now() +

            timedelta(minutes=5)

        ).isoformat()

        request.session["otp_attempts"] = 0

        send_mail(

            subject="CareerGrowza Password Reset OTP",

            message=f"""
Hello {username},

We received a request to reset your CareerGrowza password.

Your One-Time Password (OTP) is:

{otp}

This OTP is valid for 5 minutes.

If you didn't request this password reset, you can safely ignore this email.

CareerGrowza Team
""",

            from_email=settings.EMAIL_HOST_USER,

            recipient_list=[email],

            fail_silently=False,

        )

        messages.success(

            request,

            "OTP has been sent to your registered email."

        )

        return redirect("verify_otp")

    return render(

        request,

        "password/forgot_password.html"

    )


def verify_otp(request):

    if "reset_otp" not in request.session:

        messages.error(
            request,
            "Password reset session expired."
        )

        return redirect("forgot_password")

    if request.method == "POST":

        otp = "".join(
            request.POST.get(f"otp{i}", "")
            for i in range(1, 7)
        )

        if len(otp) != 6 or not otp.isdigit():

            messages.error(
                request,
                "Please enter the complete 6-digit OTP."
            )

            return render(
                request,
                "password/verify_otp.html"
            )
    
        attempts = request.session.get(
            "otp_attempts",
            0
        )

        if attempts >= 5:

            clear_reset_session(request)

            messages.error(
                request,
                "Maximum OTP attempts exceeded."
            )

            return redirect("forgot_password")

        expiry = parse_datetime(
            request.session["otp_expiry"]
        )

        if timezone.now() > expiry:

            clear_reset_session(request)

            messages.error(
                request,
                "OTP expired."
            )

            return redirect("forgot_password")

        if not check_password(
            otp,
            request.session["reset_otp"]
        ):

            request.session["otp_attempts"] = attempts + 1
            request.session.modified = True

            messages.error(
                request,
                "Incorrect OTP."
            )

            return render(
                request,
                "password/verify_otp.html"
            )

        request.session["otp_verified"] = True

        return redirect("reset_password")

    return render(
        request,
        "password/verify_otp.html"
    )


def resend_otp(request):

    username = request.session.get("reset_username")
    email = request.session.get("reset_email")

    if not username:

        return redirect("forgot_password")

    otp = str(random.randint(100000,999999))

    request.session["reset_otp"] = make_password(otp)

    request.session["otp_expiry"] = (
        timezone.now() +
        timedelta(minutes=5)
    ).isoformat()

    request.session["otp_attempts"] = 0

    send_mail(

        subject="CareerGrowza Password Reset OTP",

        message=f"""
Hello {username},

Your new OTP is

{otp}

Valid for 5 minutes.

CareerGrowza Team
""",

        from_email=settings.EMAIL_HOST_USER,

        recipient_list=[email],

        fail_silently=False,

    )

    messages.success(
        request,
        "A new OTP has been sent."
    )

    return redirect("verify_otp")

def reset_password(request):

    if not request.session.get("otp_verified"):

        messages.error(
            request,
            "OTP verification required."
        )

        return redirect("forgot_password")

    username = request.session.get("reset_username")

    try:
        profile = Profile.objects.get(
            user__username=username
        )

        user = profile.user

    except Profile.DoesNotExist:

        clear_reset_session(request)

        messages.error(
            request,
            "User not found."
        )

        return redirect("forgot_password")

    if request.method == "POST":

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "password/reset_password.html"
            )

        try:

            validate_password(password1, user)

        except ValidationError as e:

            for error in e.messages:
                messages.error(request, error)

            return render(
                request,
                "password/reset_password.html"
            )

        user.set_password(password1)
        user.save()

        # Send confirmation email
        send_mail(
            subject="CareerGrowza Password Changed",
            message=f"""
Hello {username},

Your CareerGrowza password has been changed successfully.

If you did not perform this action, please contact support immediately.

Regards,
CareerGrowza Team
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,
        )

        clear_reset_session(request)

        messages.success(
            request,
            "Password updated successfully. Please login."
        )

        return redirect("login")

    return render(
        request,
        "password/reset_password.html"
    )