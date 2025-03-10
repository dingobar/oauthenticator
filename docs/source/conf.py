# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config
# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

source = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'OAuthenticator'
copyright = 'Jupyter Contributors'
author = 'Jupyter Contributors'

root_doc = master_doc = 'index'

import oauthenticator

# The short X.Y version.
version = '%i.%i' % oauthenticator.version_info[:2]
# The full version, including alpha/beta/rc tags.
release = oauthenticator.__version__


# -- generate autodoc classes from entrypoints

from collections import defaultdict

import entrypoints
import jinja2


def render_autodoc_modules():
    authenticator_entrypoints = entrypoints.get_group_named(
        "jupyterhub.authenticators"
    ).values()

    api = os.path.join(source, "api")
    api_gen = os.path.join(api, "gen")

    # modules is a dict of dicts of lists
    # { '$module': { 'classes': [...], 'configurables': [...] } }

    modules = defaultdict(lambda: defaultdict(list))

    # pre-load base classes
    modules['oauthenticator.oauth2'] = {
        'classes': [
            'OAuthLoginHandler',
            'OAuthCallbackHandler',
        ],
        'configurables': [
            'OAuthenticator',
        ],
    }

    # load Authenticator classes from entrypoints
    for ep in authenticator_entrypoints:
        if ep.module_name and ep.module_name.startswith('oauthenticator.'):
            modules[ep.module_name]['configurables'].append(ep.object_name)

    with open(os.path.join(api, "authenticator.rst.tpl")) as f:
        tpl = jinja2.Template(f.read())

    try:
        os.makedirs(os.path.join(api_gen))
    except FileExistsError:
        pass

    for mod, mod_content in modules.items():
        dest = os.path.join(api_gen, mod + ".rst")
        print(
            "Autogenerating module documentation in {} with classes: {}".format(
                dest, mod_content
            )
        )

        with open(dest, "w") as f:
            f.write(tpl.render(module=mod, **mod_content))

    # render the module index
    with open(os.path.join(api, "index.rst.tpl")) as f:
        index_tpl = jinja2.Template(f.read())

    with open(os.path.join(api, "index.rst"), "w") as f:
        f.write(index_tpl.render(modules=modules))


render_autodoc_modules()

autodoc_mock_imports = ["tornado", "jwt", "mwoauth", "globus_sdk"]


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'autodoc_traits',
    'myst_parser',
    'sphinx_copybutton',
]

# Disable autosummary otherwise it will overwrite the oauthenticators docs in the `gen` directory.
# Reference: https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html#confval-autosummary_generate
autosummary_generate = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_book_theme'
html_title = 'OAuthenticator'

html_theme_options = {
    "repository_url": "https://github.com/jupyterhub/oauthenticator",
    "use_issues_button": True,
    "use_repository_button": True,
    "use_edit_page_button": True,
}


html_logo = '_static/images/logo/logo.png'
html_favicon = '_static/images/logo/favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Options for linkcheck builder -------------------------------------------
# ref: http://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-the-linkcheck-builder
linkcheck_ignore = [
    r"(.*)github\.com(.*)#",  # javascript based anchors
    r"(.*)/#%21(.*)/(.*)",  # /#!forum/jupyter - encoded anchor edge case
    r"https://github.com/[^/]*$",  # too many github usernames / searches in changelog
    "https://github.com/jupyterhub/oauthenticator/pull/",  # too many pull requests in changelog
    "https://github.com/jupyterhub/oauthenticator/compare/",  # too many ref comparisons in changelog
    "https://github.com/settings/applications/new",  # sign-in redirect noise
    "https://admin.google.com/",  # sign-in redirect noise
    "https://console.cloud.google.com",  # sign-in redirect noise
    "https://console.developers.google.com",  # sign-in redirect noise
]
linkcheck_anchors_ignore = [
    "/#!",
    "/#%21",
]
