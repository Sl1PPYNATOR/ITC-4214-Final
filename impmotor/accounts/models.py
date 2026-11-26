from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("regular", "Regular User"),
        ("admin", "Administrator"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="regular",
    )
    phone = models.CharField(max_length=25, blank=True)
    city = models.CharField(max_length=80, blank=True)
    bio = models.TextField(max_length=150, blank=True)

    def save(self, *args, **kwargs):
        # Keep role and Django's built-in staff/superuser flags aligned
        if self.user.is_superuser or self.user.is_staff:
            self.role = "admin"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = "admin" if (instance.is_superuser or instance.is_staff) else "regular"
        UserProfile.objects.create(user=instance, role=role)
    elif hasattr(instance, "profile"):
        instance.profile.save()