# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from typing import List

project = "promptimize"
copyright = "2023, Maxime Beauchemin"
author = "Maxime Beauchemin"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: List = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # Optional, for Google and NumPy-style docstrings
    "recommonmark",  # If you're using the recommonmark extension
]


templates_path = ["_templates"]
exclude_patterns: List = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
