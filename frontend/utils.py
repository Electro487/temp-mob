import logging

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

from .models import EmailVerificationToken, PasswordResetToken

logger = logging.getLogger(__name__)


def send_verification_email(request, user):
    """Send email verification link to user"""
    try:
        # Delete any existing unused tokens for this user
        EmailVerificationToken.objects.filter(user=user, is_used=False).delete()

        # Create new verification token
        token = EmailVerificationToken.objects.create(user=user)

        # Get current site
        current_site = get_current_site(request)

        # Build verification URL
        verification_url = request.build_absolute_uri(
            reverse("accounts:verify_email", kwargs={"token": str(token.token)})
        )

        # Email context
        context = {
            "user": user,
            "verification_url": verification_url,
            "site_name": current_site.name,
            "domain": current_site.domain,
        }

        # Render email template
        html_message = render_to_string(
            "accounts/emails/verification_email.html", context
        )
        plain_message = strip_tags(html_message)

        # Send email
        send_mail(
            subject=f"Verify your email for {current_site.name}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Verification email sent to {user.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def send_password_reset_email(request, user):
    """Send password reset link to user"""
    try:
        # Delete any existing unused tokens for this user
        PasswordResetToken.objects.filter(user=user, is_used=False).delete()

        # Create new reset token
        token = PasswordResetToken.objects.create(user=user)

        # Get current site
        current_site = get_current_site(request)

        # Build reset URL
        reset_url = request.build_absolute_uri(
            reverse(
                "accounts:password_reset_confirm", kwargs={"token": str(token.token)}
            )
        )

        # Email context
        context = {
            "user": user,
            "reset_url": reset_url,
            "site_name": current_site.name,
            "domain": current_site.domain,
        }

        # Render email template
        html_message = render_to_string(
            "accounts/emails/password_reset_email.html", context
        )
        plain_message = strip_tags(html_message)

        # Send email
        send_mail(
            subject=f"Reset your password for {current_site.name}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Password reset email sent to {user.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False


def send_welcome_email(request, user):
    """Send welcome email to newly verified user"""
    try:
        # Get current site
        current_site = get_current_site(request)

        # Email context
        context = {
            "user": user,
            "site_name": current_site.name,
            "domain": current_site.domain,
            "login_url": request.build_absolute_uri(reverse("accounts:auth")),
        }

        # Render email template
        html_message = render_to_string("accounts/emails/welcome_email.html", context)
        plain_message = strip_tags(html_message)

        # Send email
        send_mail(
            subject=f"Welcome to {current_site.name}!",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Welcome email sent to {user.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False
