from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.authz.models import Role, BusinessElement, AccessRoleRule
from apps.accounts.models import Credential, Profile
from apps.accounts.utils import hash_password
from apps.mock.models import Good, Order

User = get_user_model()

class Command(BaseCommand):
    help = "Seed demo users, roles on profiles, and a couple of goods/orders"

    def handle(self, *args, **kwargs):
        def ensure_user(email, pwd, first, role_code):
            u, created = User.objects.get_or_create(
                username=email, defaults={"email": email, "first_name": first, "is_active": True}
            )
            if created:
                Credential.objects.create(user=u, password_hash=hash_password(pwd))
                self.stdout.write(self.style.SUCCESS(f"Created user {email}"))
            prof, _ = Profile.objects.get_or_create(user=u)
            try:
                prof.role = Role.objects.get(code=role_code)
                prof.save(update_fields=["role"])
            except Role.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Role {role_code} missing"))
            return u

        admin = ensure_user("admin@local.com", "secret123", "Admin", "admin")
        user = ensure_user("user@local.com", "secret123", "User", "user")
        mgr = ensure_user("manager@local.com", "secret123", "Manager", "manager")

        # простые данные
        Good.objects.get_or_create(title="Apple", owner=user)
        Good.objects.get_or_create(title="Orange", owner=mgr)
        Order.objects.get_or_create(number="A-100", owner=user)
        Order.objects.get_or_create(number="B-200", owner=mgr)

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
