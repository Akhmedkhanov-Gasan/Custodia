.PHONY: venv install run migrate superuser lint fmt test load-fixtures seed demo

venv:
	python -m venv .venv

install:
	pip install -r requirements.txt

run:
	python src/manage.py runserver 0.0.0.0:8000

migrate:
	python src/manage.py makemigrations
	python src/manage.py migrate

superuser:
	python src/manage.py createsuperuser

lint:
	ruff check src

fmt:
	black src && isort src

test:
	pytest -q

load-fixtures:
	python src/manage.py loaddata \
	  src/fixtures/authz_roles.json \
	  src/fixtures/authz_elements.json \
	  src/fixtures/authz_rules_admin_all.json \
	  src/fixtures/authz_rules_user_manager.json \
	  src/fixtures/authz_rules_orders_user_manager.json

seed:
	python src/manage.py seed_demo

demo: load-fixtures seed run
