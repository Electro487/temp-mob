from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email read-only
        self.fields["email"].widget.attrs["readonly"] = True
        self.fields["name"].widget.attrs["placeholder"] = "Enter your full name"

    def clean_email(self):
        # Prevent email changes
        return self.instance.email

    def save(self, commit=True):
        # Combine first_name and last_name into name
        self.instance.name = f"{self.cleaned_data.get('name')}"
        return super().save(commit=commit)


class SignUpForm(UserCreationForm):
    """Custom signup form with additional fields and styling"""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "email@gmail.com",
                "id": "email",
                "name": "email",
            }
        ),
        label="Email Address",
    )

    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter your full name",
                "id": "name",
                "name": "name",
            }
        ),
        label="Full Name",
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "*************",
                "id": "signup-password",
                "name": "password",
            }
        ),
        label="Password",
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "*************",
                "id": "confirm-password",
                "name": "confirm-password",
            }
        ),
        label="Confirm Password",
    )

    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "tick-checkbox"}),
        label="Let's make it official! I agree to the Terms and Privacy Policy",
    )

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.name = self.cleaned_data["full_name"]
        # Don't activate user until email is verified
        user.is_active = False
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Custom login form"""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "email@gmail.com",
                "id": "login-email",
                "name": "email",
            }
        ),
        label="Email Address",
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "*************",
                "id": "login-password",
                "name": "password",
            }
        ),
        label="Password",
    )


class PasswordResetRequestForm(forms.Form):
    """Form for requesting password reset"""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter your email address",
                "id": "reset-email",
                "name": "email",
            }
        ),
        label="Email Address",
        help_text="Enter your email address.",
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No account found with this email.")
        return email


class PasswordResetConfirmForm(forms.Form):
    """Form for confirming password reset with new password"""

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter new password",
                "id": "new-password",
                "name": "password1",
            }
        ),
        label="New Password",
        min_length=8,
        help_text="Your password must be at least 8 characters long.",
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Confirm new password",
                "id": "confirm-new-password",
                "name": "password2",
            }
        ),
        label="Confirm New Password",
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password didn't match.")
        return password2


class ResendVerificationForm(forms.Form):
    """Form for resending email verification"""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter your email address",
                "id": "verification-email",
                "name": "email",
            }
        ),
        label="Email Address",
        help_text="Enter your email address to resend verification link.",
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            user = User.objects.get(email=email)
            if user.is_verified_email:  # type: ignore
                raise forms.ValidationError("This email address is already verified.")
        except User.DoesNotExist:
            raise forms.ValidationError("No account found with this email address.")
        return email
