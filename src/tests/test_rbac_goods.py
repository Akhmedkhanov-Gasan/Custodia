import pytest
from rest_framework.test import APIClient
from apps.mock.models import Good

@pytest.mark.django_db
def test_user_sees_only_own_goods(user, manager, bearer):
    Good.objects.create(title="U1", owner=user)
    Good.objects.create(title="M1", owner=manager)
    c = APIClient()
    c = bearer(c, user)
    r = c.get("/api/mock/goods/")
    assert r.status_code == 200
    titles = [x["title"] for x in r.data]
    assert "U1" in titles and "M1" not in titles

@pytest.mark.django_db
def test_manager_reads_all_updates_only_own(user, manager, bearer):
    g_u = Good.objects.create(title="U1", owner=user)
    g_m = Good.objects.create(title="M1", owner=manager)
    c = APIClient()
    c = bearer(c, manager)

    # list: sees both
    r = c.get("/api/mock/goods/")
    assert r.status_code == 200 and len(r.data) == 2

    # patch own -> 200
    r = c.patch(f"/api/mock/goods/{g_m.id}/", {"title": "OWN"}, format="json")
    assert r.status_code == 200

    # patch foreign -> 403
    r = c.patch(f"/api/mock/goods/{g_u.id}/", {"title": "NOPE"}, format="json")
    assert r.status_code == 403
