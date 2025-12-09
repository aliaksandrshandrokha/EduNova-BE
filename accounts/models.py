from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """User profile model with additional user information."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    full_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        db_table = 'accounts_profile'

