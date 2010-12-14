# Makefile for Sy
#

.PHONY: test docs publish_docs readme pypi publish

test:
	@(nosetests -a "!host" tests)

doctest:
	@(cd docs; sphinx-build -b doctest . _build/doctest)

docs:
	@(cd docs; make html)
	@(cp docs/_gae/* docs/_build)

publish_docs: docs
	@(appcfg.py update docs/_build)

readme:
	@(cat docs/readme_head.rst docs/intro.rst > README.rst)
	@echo "Copied docs/readme_head and intro.rst to README.rst"

egg: readme 
	@(python setup.py bdist_egg release)
 
pypi: readme 
	@(python setup.py bdist_egg release upload)

publish: test pypi publish_docs
	@echo "Published new release"

