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

.PHONY: push-git
push-git:
	git push origin
	git push github-mirror
