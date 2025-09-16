from django.contrib import admin
from .models import Credential, Profile

@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = ("user",)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "patronymic")
