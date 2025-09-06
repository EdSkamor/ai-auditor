# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Custom targets
clean:
	rm -rf $(BUILDDIR)/*
	rm -rf $(SOURCEDIR)/_static/custom.css

html: clean
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html/."

pdf:
	@$(SPHINXBUILD) -M latexpdf "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Build finished. The PDF is in $(BUILDDIR)/latex/."

serve: html
	cd $(BUILDDIR)/html && python -m http.server 8000
	@echo "Documentation server running at http://localhost:8000"

watch: html
	@echo "Watching for changes..."
	@while true; do \
		inotifywait -e modify,create,delete -r $(SOURCEDIR)/; \
		$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O); \
	done

install:
	pip install sphinx sphinx-rtd-theme

setup: install
	mkdir -p $(SOURCEDIR)/_static
	@echo "/* Custom styles for AI Auditor documentation */" > $(SOURCEDIR)/_static/custom.css
	@echo "body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }" >> $(SOURCEDIR)/_static/custom.css
	@echo ".wy-side-nav-search { background-color: #2E8B57; }" >> $(SOURCEDIR)/_static/custom.css
	@echo ".wy-nav-top { background-color: #2E8B57; }" >> $(SOURCEDIR)/_static/custom.css

