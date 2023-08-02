setup-dev:
	python -m venv .venv
	.venv/bin/python -m pip install -U pip
	.venv/bin/pip install -r requirements-dev.txt

build:
	.venv/bin/python -m build

typecheck:
	.venv/bin/mypy
