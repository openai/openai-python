.PHONY: build upload

build:
	OPENAI_UPLOAD=y python setup.py sdist

upload:
	OPENAI_UPLOAD=y twine upload dist/*
