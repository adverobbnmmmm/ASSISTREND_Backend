from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone  # Added import


class CustomUser(AbstractUser):
    # Remove username field (we'll use email as primary identifier)
    username = models.CharField(
        _("username"),
        max_length=150,
        blank=True,
        null=True,
        help_text=_("Optional. 150 characters or fewer."),
    )

    # Make email unique and required
    email = models.EmailField(_("email address"), unique=True)

    # Social auth fields
    bio = models.TextField(_("bio"), max_length=500, blank=True)
    profile_picture = models.URLField(_("profile picture"), blank=True)
    social_provider = models.CharField(
        _("social provider"),
        max_length=20,
        blank=True,
        help_text=_("The social platform used for registration (e.g., google)"),
    )
    social_uid = models.CharField(
        _("social UID"),
        max_length=200,
        blank=True,
        help_text=_("User ID from social provider"),
    )

    # Additional useful fields
    email_verified = models.BooleanField(_("email verified"), default=False)
    created_at = models.DateTimeField(_("created at"), default=timezone.now)  # Changed from auto_now_add
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    # Set email as the USERNAME_FIELD
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Remove email from REQUIRED_FIELDS since it's USERNAME_FIELD

    def __str__(self):
        return self.email or self.social_uid

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")