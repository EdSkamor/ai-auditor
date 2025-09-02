project = 'Asystent Audytora'
author = 'Zespół'
extensions = ['myst_parser','sphinx.ext.autodoc','sphinx.ext.viewcode', 'sphinx_design']
templates_path = ['_templates']
exclude_patterns = []
html_theme = 'sphinx_rtd_theme'
myst_enable_extensions = ["deflist","colon_fence"]
html_title = 'Asystent Audytora — Dokumentacja'
html_static_path = ['_static']

html_context = {'display_github': False}

def setup(app):
    app.add_css_file('custom.css')
