from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.authz.models import Role


class Credential(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cred"
    )
    password_hash = models.CharField(max_length=200)

    def __str__(self) -> str:
        return f"cred:{self.user_id}"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    patronymic = models.CharField(max_length=150, blank=True, default="")

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="profiles",
    )

    def __str__(self) -> str:
        return f"profile:{self.user_id}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def _ensure_profile(sender, instance, created, **kwargs):
    if created:
        profile, _ = Profile.objects.get_or_create(user=instance)
        if profile.role_id is None:
            try:
                profile.role = Role.objects.get(code="user")
                profile.save(update_fields=["role"])
            except Role.DoesNotExist:
                pass
