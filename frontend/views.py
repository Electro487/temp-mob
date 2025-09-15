# from django.shortcuts import render

# # Create your views here.
# def auth_view(request):
#     return render(request, "frontend/auth.html")

from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.urls import reverse

from frontend.forms import (LoginForm, PasswordResetConfirmForm,
                            PasswordResetRequestForm, ProfileUpdateForm,
                            ResendVerificationForm, SignUpForm)
from frontend.services import (confirm_password_reset, handle_login,
                               handle_signup, request_password_reset,
                               resend_verification, verify_email_token)
from frontend.utils import send_welcome_email


@login_required
def dashboard_view(request):
    return render(request, "frontend/dashboard.html", {"user": request.user})


def auth_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    signup_form = SignUpForm()
    login_form = LoginForm()
    show_login = False

    if request.method == "POST":
        if "signup_form" in request.POST:
            signup_form = SignUpForm(request.POST)
            if signup_form.is_valid():
                result = handle_signup(request, signup_form)
                if result == "resend":
                    messages.info(
                        request, "Verification email resent. Please check your inbox."
                    )
                    return redirect("frontend:verification_sent")
                elif result == "exists":
                    messages.error(request, "Email already registered.")
                elif result == "success":
                    return redirect("frontend:verification_sent")
                else:
                    messages.error(
                        request,
                        "Account created but email failed to send. Contact support.",
                    )

        elif "login_form" in request.POST:
            login_form = LoginForm(request.POST)
            show_login = True
            if login_form.is_valid():
                user, status = handle_login(request, login_form)
                if status == "success":
                    login(request, user)
                    messages.success(request, f"Successfully signed in as {user.name}")  # type: ignore
                    return redirect("home")
                elif status == "unverified":
                    messages.error(
                        request,
                        "Please verify your email first. "
                        f"<a href='{reverse('frontend:resend_verification')}'>Resend</a>",
                    )
                elif status == "inactive":
                    messages.error(
                        request,
                        "Your account has been deactivated. Please contact support.",
                    )
                else:
                    messages.error(request, "Invalid email or password.")

    return render(
        request,
        "frontend/auth.html",
        {
            "signup_form": signup_form,
            "login_form": login_form,
            "show_login": show_login,
        },
    )


def verify_email_view(request, token):
    user, status = verify_email_token(token)
    if status == "expired":
        messages.error(request, "Verification link expired. Request a new one.")
        return redirect("frontend:resend_verification")
    elif status == "used":
        messages.error(request, "This verification link has already been used.")
        return redirect("frontend:auth")
    elif status == "success":
        send_welcome_email(request, user)
        messages.success(request, "Your email has been verified! You can now log in.")
        return redirect("frontend:auth")

    messages.error(request, "Invalid verification link.")
    return redirect("frontend:auth")


def verification_sent_view(request):
    return render(request, "frontend/emails/verification_sent.html")


def resend_verification_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = ResendVerificationForm(request.POST)
        if form.is_valid():
            if resend_verification(request, form.cleaned_data["email"]):
                messages.success(
                    request, "Verification email sent. Please check your inbox."
                )
                return redirect("frontend:verification_sent")
            messages.error(request, "Failed to send verification email.")
    else:
        form = ResendVerificationForm()
    return render(request, "frontend/emails/resend_verification.html", {"form": form})


def password_reset_request_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            user, status = request_password_reset(request, form.cleaned_data["email"])
            if status == "unverified":
                messages.error(request, "Please verify your email address first.")
                return redirect("frontend:resend_verification")
            elif status == "success":
                messages.success(
                    request, "Password reset instructions sent to your email."
                )
                return redirect("frontend:password_reset_sent")
            elif status == "fail":
                messages.error(
                    request, "Failed to send password reset email. Try again later."
                )
            else:
                messages.error(request, "Invalid email address.")
    else:
        form = PasswordResetRequestForm()

    return render(
        request, "frontend/emails/password_reset_request.html", {"form": form}
    )


def password_reset_sent_view(request):
    return render(request, "frontend/emails/password_reset_sent.html")


def password_reset_confirm_view(request, token):
    if request.method == "POST":
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            user, status = confirm_password_reset(token, form.cleaned_data["password1"])
            if status == "success":
                messages.success(
                    request, "Your password has been reset. You can log in now."
                )
                return redirect("frontend:auth")
            elif status == "expired":
                messages.error(request, "Password reset link expired.")
                return redirect("frontend:password_reset")
            elif status == "used":
                messages.error(
                    request, "This password reset link has already been used."
                )
                return redirect("frontend:password_reset")
            else:
                messages.error(request, "Invalid password reset link.")
                return redirect("frontend:password_reset")
    else:
        form = PasswordResetConfirmForm()

    return render(
        request,
        "frontend/emails/password_reset_confirm.html",
        {"form": form, "token": token},
    )


@login_required
def profile_view(request):
    profile_form = ProfileUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    if request.method == "POST":
        if "update_profile" in request.POST:
            profile_form = ProfileUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Your profile has been updated successfully!")
                return redirect("profile")
            messages.error(
                request, "Please correct the errors in your profile information."
            )

        elif "change_password" in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(
                    request, "Your password has been changed successfully!"
                )
                return redirect("profile")
            messages.error(request, "Please correct the errors in your password form.")

    return render(
        request,
        "frontend/profile.html",
        {
            "profile_form": profile_form,
            "password_form": password_form,
        },
    )
