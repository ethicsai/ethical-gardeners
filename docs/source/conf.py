# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# Because the modules we want to document are in another directory, we must
# add them to sys.path ; we also use os.path.abspath to transform the relative
# path into an absolute one.
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'EthicalGardeners'
copyright = '2025, Enzo Dos Anjos, Remy Chaput'
author = 'Enzo Dos Anjos, Remy Chaput'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Include documentation from docstrings
    'sphinx.ext.autodoc',
    # Generate summaries (tables/listings) for autodoc
    'sphinx.ext.autosummary',
    # Link to external (other projects') documentation
    'sphinx.ext.intersphinx',
    # Automatically add a 'copy button' to our code blocks
    'sphinx_copybutton',
    # Add a link to the source code on each of the "API pages"
    'sphinx.ext.viewcode',
    # Render the docs for multiple versions (tags, branches, ...)
    'sphinx_multiversion',
]

# Enable autosummary
autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = []

# Mapping to other projects
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'gymnasium': ('https://gymnasium.farama.org/', None),
}

# -- Sphinx-multiversion configuration ---------------------------------------
# https://sphinx-contrib.github.io/multiversion/main/index.html

# Accept all branches except:
# - any `wip/**` branch (because they are not ready)
smv_branch_whitelist = r'^(?!wip/).*'

# Allow remote branches from `origin` only (required for building all branches
# on GitHub Actions, because they are not automatically fetched).
smv_remote_whitelist = r'^origin$'

# A version is considered "released" only if it is a tag beginning with `v`.
smv_released_pattern = r'^tags/v.*$'

# Each version gets a subdir based on its name (e.g., `master`, `v1.0.0`, ...)
smv_outputdir_format = '{ref.name}'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']

# Override Furo's default sidebar widgets to add our version selector
# At some point we should be able to use `variant-selector`, when Furo will add
# support for versions.
html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "versioning.html",  # Our custom template
        "sidebar/navigation.html",
        "sidebar/ethical-ads.html",
        "sidebar/variant-selector.html",
        "sidebar/scroll-end.html",
    ]
}
