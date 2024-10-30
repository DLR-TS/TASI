# import recommonmark
# from recommonmark.transform import AutoStructify

import sys, os
import warnings


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "IPython.sphinxext.ipython_console_highlighting",
    "IPython.sphinxext.ipython_directive",
    "sphinx_gallery.load_style",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.linkcode",
    "myst_parser",
    "nbsphinx",
    "numpydoc",
    "sphinx_toggleprompt",
    "matplotlib.sphinxext.plot_directive",
]


# continue doc build and only print warnings/errors in examples
ipython_warning_is_error = False
ipython_exec_lines = [
    # ensure that dataframes are not truncated in the IPython code blocks
    "import pandas as _pd",
    '_pd.set_option("display.max_columns", 20)',
    '_pd.set_option("display.width", 100)',
]

# Fix issue with warnings from numpydoc (see discussion in PR #534)
numpydoc_show_class_members = False
autodoc_typehints = "none"


# Add any paths that contain templates here, relative to this directory.

templates_path = ["_templates"]


autosummary_generate = True

nbsphinx_execute = "always"
nbsphinx_allow_errors = True
nbsphinx_kernel_name = "python3"

# suppress matplotlib warning in examples
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="Matplotlib is currently using agg, which is a"
    " non-GUI backend, so cannot show the figure.",
)

# The suffix of source filenames.
source_suffix = [".rst"]


# The master toctree document.
master_doc = "index"

# General information about the project.
project = "TASI"
copyright = "2024-, DLR TS and contributors"


# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
import tasi

release = release = tasi.__version__
version = release
if "+" in version:
    version, remainder = release.split("+")
    if not remainder.startswith("0"):
        version = version + ".dev+" + remainder.split(".")[0]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "pydata_sphinx_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/dlr-ts/tasi",
            "icon": "fab fa-github-square fa-xl",
        },
        {
            "name": "DLR",
            "url": "https://dlr.de/ts/en/",
            "icon": "fa-custom fa-dlr",
            "type": "fontawesome"
        },
    ]
}

html_title = project

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# Add redirect for previously existing pages, each item is like `(from_old, to_new)`

html_js_files = [
    "logos/DLR_black.js"
]

nbsphinx_prolog = r"""
{% set docname = env.doc2path(env.docname, base=None) %}

.. only:: html

    .. role:: raw-html(raw)
        :format: html

    .. note::

        | This page was generated from `{{ docname }}`__.
        | Interactive online version: :raw-html:`<a href="https://mybinder.org/v2/gh/dlr-ts/tasi/main?urlpath=lab/tree/doc/source/{{ docname }}"><img alt="Binder badge" src="https://mybinder.org/badge_logo.svg" style="vertical-align:text-bottom"></a>`

        __ https://github.com/dlr-ts/tasi/blob/main/doc/source/{{ docname }}
"""

#  --Options for sphinx extensions -----------------------------------------------

# connect docs in other projects
intersphinx_mapping = {
    "folium": (
        "https://python-visualization.github.io/folium/latest",
        "https://python-visualization.github.io/folium/latest/objects.inv",
    ),
    "matplotlib": (
        "https://matplotlib.org/stable/",
        "https://matplotlib.org/stable/objects.inv",
    ),
    "pandas": (
        "https://pandas.pydata.org/pandas-docs/stable/",
        "https://pandas.pydata.org/pandas-docs/stable/objects.inv",
    ),
    "python": (
        "https://docs.python.org/3",
        "https://docs.python.org/3/objects.inv",
    ),
    "shapely": (
        "https://shapely.readthedocs.io/en/stable/",
        "https://shapely.readthedocs.io/en/stable/objects.inv",
    ),
}


def setup(app):
    app.add_css_file("custom.css")  # may also be an URL

# based on pandas implementation with added support of properties
def linkcode_resolve(domain, info):
    """
    Determine the URL corresponding to Python object
    """
    import inspect

    if domain != "py":
        return None

    modname = info["module"]
    fullname = info["fullname"]

    submod = sys.modules.get(modname)
    if submod is None:
        return None

    obj = submod
    for part in fullname.split("."):
        try:
            with warnings.catch_warnings():
                # Accessing deprecated objects will generate noisy warnings
                warnings.simplefilter("ignore", FutureWarning)
                obj = getattr(obj, part)
        except AttributeError:
            return None

    try:
        fn = inspect.getsourcefile(inspect.unwrap(obj))
    except TypeError:
        try:  # property
            fn = inspect.getsourcefile(inspect.unwrap(obj.fget))
        except AttributeError:
            fn = None
    if not fn:
        return None

    try:
        source, lineno = inspect.getsourcelines(obj)
    except TypeError:
        try:  # property
            source, lineno = inspect.getsourcelines(obj.fget)
        except AttributeError:
            lineno = None
    except OSError:
        lineno = None

    if lineno:
        linespec = f"#L{lineno}-L{lineno + len(source) - 1}"
    else:
        linespec = ""

    fn = os.path.relpath(fn, start=os.path.dirname(tasi.__file__))

    if "+" in tasi.__version__:
        return (
            f"https://github.com/dlr-ts/tasi/blob/main/tasi/{fn}{linespec}"
        )
    else:
        return (
            f"https://github.com/dlr-ts/tasi/blob/"
            f"v{tasi.__version__}/tasi/{fn}{linespec}"
        )
