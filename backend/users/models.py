from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Inherit from AbstractUser and make first_name, last_name and email
     required.
    """
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

    class Meta:
        ordering = ['id']


class Subscription(models.Model):
    """Implement 'following' possibility.

    Any user can follow any user get easy navigated to its recipes."""
    user = models.ForeignKey(
        User, related_name='subscriptions',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User, related_name='subscribers',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['id']
