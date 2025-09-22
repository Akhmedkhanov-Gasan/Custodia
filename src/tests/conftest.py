import pathlib
import pytest
from django.core.management import call_command
from django.contrib.auth import get_user_model
from apps.accounts.models import Credential, Profile
from apps.accounts.utils import hash_password, make_access
from apps.authz.models import Role

User = get_user_model()

@pytest.fixture(scope="session", autouse=True)
def _load_base_fixtures(django_db_setup, django_db_blocker):
    here = pathlib.Path(__file__).resolve()
    repo_root = here.parents[2]
    fixtures = [
        repo_root / "src" / "fixtures" / "authz_roles.json",
        repo_root / "src" / "fixtures" / "authz_elements.json",
        repo_root / "src" / "fixtures" / "authz_rules_admin_all.json",
        repo_root / "src" / "fixtures" / "authz_rules_user_manager.json",
        repo_root / "src" / "fixtures" / "authz_rules_orders_user_manager.json",
        ]
    with django_db_blocker.unblock():
        call_command("loaddata", *map(str, fixtures))

@pytest.fixture
def user(db):
    u = User.objects.create(username="u@test.com", email="u@test.com", is_active=True)
    Credential.objects.create(user=u, password_hash=hash_password("secret123"))
    p, _ = Profile.objects.get_or_create(user=u)
    p.role = Role.objects.get(code="user")
    p.save()
    return u

@pytest.fixture
def manager(db):
    u = User.objects.create(username="m@test.com", email="m@test.com", is_active=True)
    Credential.objects.create(user=u, password_hash=hash_password("secret123"))
    p, _ = Profile.objects.get_or_create(user=u)
    p.role = Role.objects.get(code="manager")
    p.save()
    return u

@pytest.fixture
def admin(db):
    u = User.objects.create(
        username="a@test.com",
        email="a@test.com",
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )
    Credential.objects.create(user=u, password_hash=hash_password("secret123"))
    p, _ = Profile.objects.get_or_create(user=u)
    p.role = Role.objects.get(code="admin")
    p.save()
    return u

@pytest.fixture
def bearer():
    from apps.accounts.utils import make_access
    def _bearer(client, user):
        client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {make_access(user.id)}"
        return client
    return _bearer
