.PHONY: setup-dev
setup-dev:
	python ./dagrun.py -f dags/setup_dev.py

.PHONY: build
build:
	.venv/bin/python -m build

.PHONY: typecheck
typecheck:
	.venv/bin/mypy

.PHONY: git-push
git-push:
	git push origin
	git push --tags origin
	git push github-mirror
	git push --tags github-mirror
