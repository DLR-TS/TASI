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
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.linkcode",
    "sphinx.ext.napoleon",
    "myst_parser",
    "nbsphinx",
    "sphinx_toggleprompt",
    "matplotlib.sphinxext.plot_directive",
    "sphinxemoji.sphinxemoji",
]


napoleon_google_docstring = True

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
numfig = True
templates_path = ["_templates"]

autosummary_generate = True

nbsphinx_execute = "always"
nbsphinx_allow_errors = True
nbsphinx_kernel_name = "python3"

graphviz_output_format = "svg"

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

header = f"""\
.. currentmodule:: tasi

.. ipython:: python
   :suppress:

   import numpy as np
   import pandas as pd

   np.random.seed(123456)
   np.set_printoptions(precision=4, suppress=True)
   pd.options.display.max_rows = 15

   import os
   os.chdir(r'{os.path.dirname(os.path.dirname(__file__))}')
"""

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
            "type": "fontawesome",
        },
    ]
}


html_context = {
    "header": header,
}

html_title = project

html_sidebars = {"about": [], "development/index": [], "getting_started/index": []}

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

html_js_files = ["logos/DLR_black.js"]

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
    "matplotlib": (
        "https://matplotlib.org/stable/",
        "_static/invs/matplotlib.inv",
    ),
    "pandas": (
        "https://pandas.pydata.org/pandas-docs/stable/",
        "_static/invs/pandas.inv",
    ),
    "python": (
        "https://docs.python.org/3",
        "_static/invs/python.inv",
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
        return f"https://github.com/dlr-ts/tasi/blob/main/tasi/{fn}{linespec}"
    else:
        return (
            f"https://github.com/dlr-ts/tasi/blob/"
            f"v{tasi.__version__}/tasi/{fn}{linespec}"
        )


# -- Options for nbsphinx ------------------------------------------------
import os
import jinja2

nbsphinx_allow_errors = False

# If false, no module index is generated.
html_use_modindex = True

# convert all cell-based jupyter notebooks
SOURCE_PATH = os.path.dirname(os.path.abspath(__file__))

nbsphinx_custom_formats = {
    ".pct.py": ["jupytext.reads", {"fmt": "py:percent"}],
}

# allow raw HTML in your documentation
myst_allow_raw_html = True
html_js_files = ["https://cdn.jsdelivr.net/npm/folium@latest/dist/folium.min.js"]

# render the index templates in the user-guide

for section in ["user_guide", "getting_started"]:

    section_path = os.path.join(SOURCE_PATH, "user_guide")

    if os.path.exists(section_path):

        for section in [
            d
            for d in os.listdir(section_path)
            if os.path.isdir(os.path.join(section_path, d))
        ]:

            # the target directory for the jupyter notebooks
            notebook_path = os.path.join(section_path, section)

            # list up all notebooks
            NOTEBOOKS = [
                f
                for f in os.listdir(notebook_path)
                if f.endswith(".pct.py") or (f.endswith(".rst") and "index" not in f)
            ]

            # taken from https://github.com/pandas-dev/pandas/blob/c45e92c3956fd2638980ac46e6e93ec3b6cc7c52/doc/source/conf.py#L87
            with open(os.path.join(notebook_path, "index.rst.template")) as f:
                t = jinja2.Template(f.read())

            with open(os.path.join(notebook_path, "index.rst"), "w") as f:
                f.write(t.render(examples="\n".join(sorted(NOTEBOOKS))))
