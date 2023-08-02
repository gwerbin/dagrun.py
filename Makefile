.PHONY: setup-dev
setup-dev:
	python -m venv .venv
	.venv/bin/python -m pip install -U pip
	.venv/bin/pip install -r requirements-dev.txt
	.venv/bin/pip install -e .

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
