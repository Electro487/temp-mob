from datetime import timedelta

from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone

from frontend.models import EmailVerificationToken, PasswordResetToken
from frontend.utils import send_password_reset_email, send_verification_email

User = get_user_model()

# ---------------- AUTH / SIGNUP / LOGIN ----------------


def handle_signup(request, form):
    """Process signup form logic"""
    email = form.cleaned_data.get("email")
    existing_user = User.objects.filter(email=email).first()

    if existing_user:
        if not existing_user.is_verified_email:  # type: ignore
            if existing_user.created_at < timezone.now() - timedelta(hours=24):  # type: ignore
                existing_user.delete()
            else:
                send_verification_email(request, existing_user)
                return "resend"  # signal to resend email
        else:
            return "exists"

    user = form.save()
    if send_verification_email(request, user):
        return "success"
    return "fail"


def handle_login(request, form):
    """Process login form logic"""
    email = form.cleaned_data["email"]
    password = form.cleaned_data["password"]

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None, "invalid"

    if not user.is_verified_email:  # type: ignore
        return user, "unverified"

    if not user.is_active:
        return user, "inactive"

    user = authenticate(request, email=email, password=password)
    if not user:
        return None, "invalid"

    return user, "success"


# ---------------- EMAIL VERIFICATION ----------------


def verify_email_token(token):
    """Validate and consume verification token"""
    try:
        verification_token = EmailVerificationToken.objects.get(token=token)
    except EmailVerificationToken.DoesNotExist:
        return None, "invalid"

    if verification_token.is_expired():
        return None, "expired"

    if verification_token.is_used:
        return None, "used"

    user = verification_token.user
    user.is_verified_email = True
    user.is_active = True
    user.save()

    verification_token.is_used = True
    verification_token.save()

    return user, "success"


def resend_verification(request, email):
    """Resend email verification link"""
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return False

    return send_verification_email(request, user)


# ---------------- PASSWORD RESET ----------------


def request_password_reset(request, email):
    """Send password reset email if user is verified"""
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None, "invalid"

    # If not verified and created more than 24 hours ago → delete
    if not user.is_verified_email and user.created_at < timezone.now() - timedelta(hours=24) : # type: ignore
        user.delete()
        return None, "Your account exceed the time limit for verification. Please register again."

    if not user.is_verified_email: # type: ignore
        return user, "Email not verified. Please verify it."
    
    if send_password_reset_email(request, user):
        return user, "success"
    return None, "fail"


def confirm_password_reset(token, new_password):
    """Confirm password reset via token and set new password"""
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        return None, "invalid"

    if reset_token.is_expired():
        return None, "expired"

    if reset_token.is_used:
        return None, "used"

    user = reset_token.user
    user.set_password(new_password)
    user.save()

    reset_token.is_used = True
    reset_token.save()

    return user, "success"
