run:
	python app.py

test:
	python -m nose --verbosity=3 -x --with-xunit --rednose

coverage:
	coverage run --source=i18n,lib,routes,services -m nose --verbosity=3 -x --with-xunit --rednose
	coverage report -m

watch:
	fswatch -d -e i18n/__pycache__ -e lib/__pycache__ -e routes/__pycache__ -e services/__pycache__ -e tests/**/__pycache__ contentful tests | xargs -n1 make coverage

lint:
	flake8 --exclude=tests --show-source
