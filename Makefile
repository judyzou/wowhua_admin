.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "config - install config and scripts in virtualenv"
	@echo "coverage - run coverage test"
	@echo "lint - check style with pylint"
	@echo "utest - run utests"
	@echo "ftest - run ftests"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "sdist - package"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

init: config
	pip install -e .[develop]

config:
	mkdir -p $(VIRTUAL_ENV)/etc
	-rm -f $(VIRTUAL_ENV)/etc/wowhua_admin.*
	-rm -f $(VIRTUAL_ENV)/etc/wowhua_admin_spec.*
	ln -s `pwd`/wowhua_admin/conf/* $(VIRTUAL_ENV)/etc/
	pip install -e .[test]

lint:
	pylint --rcfile=.pylint.rc wowhua_admin utests ftests

start:
	python scripts/manage.py runserver

stop:
	ps aux | grep -v grep | grep manage.py | awk '{print $$2}' | xargs kill > /dev/null 2>&1 || exit 0


test_depends: l10n_update l10n_compile

utest: clean
	py.test -v --cov-report term --cov wowhua_admin tests

ftest_clean:
	#init_schema.py -r -a -t >/dev/null 2>&1
	python scripts/manage.py reset_db

ftest: ftest_clean clean
	py.test -v ftests

test: utest ftest

coverage: clean test_depends
	py.test -v --cov-report html --cov wowhua_admin tests
	open htmlcov/index.html

docs:
	rm -f docs/wowhua_admin.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ wowhua_admin
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	@echo "open docs/_build/html/index.html"

release: docs clean test ftest
	python setup.py sdist upload -r zchpi

sdist: docs clean test ftest
	python setup.py sdist
	ls -l dist

l10n_extract:
	pybabel extract -F babel/babel.cfg -k _gettext -k _ngettext -k lazy_gettext -o babel/admin.pot --project WH-Admin wowhua_admin

l10n_init: l10n_extract
	pybabel init -i babel/admin.pot -d ../wowhua_admin/translations -l zh_CN

l10n_update: l10n_extract
	pybabel update -i babel/admin.pot -d wowhua_admin/translations
	python wowhua_admin/translations/clean_po.py

l10n_compile:
	pybabel compile -f -d wowhua_admin/translations

# docker need sudo permission on ubuntu
#
docker_build:
	fig build web

docker_run:
	fig up

docker_ci:
	fig run web bash ci_script.sh --rm
	fig stop

docker_initdb:
	# after docker_run
	#fig run web /testenv/bin/python scripts/init_mock_data.py
	fig run web /testenv/bin/python scripts/manage.py reset_db

docker_init_permission:
	# after user login
	fig run web /testenv/bin/python scripts/manage.py reset_permission

docker_push:
	docker tag wowhuaadmin_web docker-registry.lxdb.jiake.org/wowhua_admin
	docker push docker-registry.lxdb.jiake.org/wowhua_admin

reset_db:
	python scripts/manage.py reset_db

reset_permission:
	python scripts/manage.py reset_permission
