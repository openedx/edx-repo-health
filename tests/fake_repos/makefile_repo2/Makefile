.DEFAULT_GOAL := help
NODE_BIN=./node_modules/.bin
TOX = ''

.PHONY: clean requirements piptools upgrade quality isort_check format_check quality-js tests js-tests

clean: ## Remove all generated files
	coverage erase
	find . -path '*/__pycache__/*' -delete
	find . -name \*.pyc -o -name \*.pyo -o -name __pycache__ -delete

requirements: piptools ## Install requirements for local development
	npm install --also=dev
	pip-sync requirements/dev.txt

piptools:
	pip install -q -r requirements/pip_tools.txt

export CUSTOM_COMPILE_COMMAND = make upgrade
upgrade: piptools ## update the requirements/*.txt files with the latest packages satisfying requirements/*.in
	pip-compile --rebuild --upgrade -o requirements/pip-tools.txt requirements/pip-tools.in
	pip-compile --allow-unsafe --rebuild --upgrade -o requirements/pip.txt requirements/pip.in
	pip install -qr requirements/pip.txt
	pip install -qr requirements/pip-tools.txt
	pip-compile --rebuild --upgrade -o requirements/base.txt requirements/base.in
	pip-compile --rebuild --upgrade -o requirements/test.txt requirements/test.in
	pip-compile --rebuild --upgrade -o requirements/docs.txt requirements/docs.in
	pip-compile --rebuild --upgrade -o requirements/dev.txt requirements/dev.in
	pip-compile --rebuild --upgrade -o requirements/production.txt requirements/production.in
	pip-compile --rebuild --upgrade -o requirements/all.txt requirements/all.in
	# Let tox control the Django version for tests
	grep -e "^django==" requirements/production.txt > requirements/django.txt
	sed '/^[dD]jango==/d' requirements/test.txt > requirements/test.tmp
	mv requirements/test.tmp requirements/test.txt

### Quality commands ###

quality: isort_check quality-js format_check ## Run linters
	pylint --django-settings-module=makefile_repo2.settings.test --rcfile=pylintrc acceptance_tests makefile_repo2 *.py

isort_check: ## Check that isort has been run
	isort --check-only acceptance_tests/ makefile_repo2/

format_check: ## check that code is formatted correctly
	black --check .

quality-js: ## Run JavaScript linter
	$(NODE_BIN)/gulp lint

### Testing commands ###

tests: ## Run tests and generate coverage report
	$(TOX)coverage run -m pytest --ds makefile_repo2.settings.test --durations=25
	$(TOX)coverage report
	make js-tests

js-tests: ## Run javascript tests
	$(NODE_BIN)/gulp test
	npm run test-react
