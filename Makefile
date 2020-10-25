.PHONY: build upload

build:
	python setup.py sdist

upload:
	twine upload dist/openai-*.tar.gz
	rm dist/openai-*.tar.gz

