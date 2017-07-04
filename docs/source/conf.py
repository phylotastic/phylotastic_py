# -*- coding: utf-8 -*-
#
# Phylotastic-services documentation build configuration file, created by
# sphinx-quickstart on Mon Jun 26 11:31:37 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
    'sphinx.ext.coverage']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Phylotastic-services'
copyright = u'2017, Abu Saleh Md Tayeen'
author = u'Abu Saleh Md Tayeen'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = u'0.1'
# The full version, including alpha/beta/rc tags.
release = u'0.1'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'Phylotastic-servicesdoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'Phylotastic-services.tex', u'Phylotastic-services Documentation',
     u'Abu Saleh Md Tayeen', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'phylotastic-services', u'Phylotastic-services Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'Phylotastic-services', u'Phylotastic-services Documentation',
     author, 'Phylotastic-services', 'The Phylotastic project aims to lower the barriers to accessing the tree of life: to make getting a species tree just as easy.',
     'Miscellaneous'),
]

# ---- Skip member functions -------------------------------------------------
def autodoc_skip_member(app, what, name, obj, skip, options):
    exclusions = ('__main__',  # special-members
                  'get_sn_text', 'get_token_result', 'is_ascii', 'get_sn', 'get_sn_url',  # undoc-members
                  'create_sublists', 'get_resolved_names', 'resolve_sn_ot', 'make_api_friendly_list', 'resolve_sn_gnr',
'get_inducedSubtree','subtree','get_tree_OT','get_supporting_studies','get_num_tips','get_tree_version', 'get_metadata', 'get_phylomatic_tree','get_taxa_context','get_contexts', 'process_phylomatic_result', 'get_tree_phyloMT','find_taxon_id', 'get_tree_itol', 'get_ncbi_ids', 'create_file_input_ids', 'get_tree_phyloT', 'match_taxon', 'get_children', 'get_species_from_highrank', 'get_species_from_genus', 'check_species_by_country', 'form_cs_ids', 'get_species_names', 'find_species_ids', 'find_genome_ids','match_species', 'get_species_info', 'get_imageObjects', 'create_image_obj', 'get_image_species_id', 'get_ott_ids', 'get_studies_from_ids', 'get_studies', 'get_study_info', 'get_study_ids','ComplexEncoder','reprJSON')
    exclude = name in exclusions
    return skip or exclude

def setup(app):
    app.connect('autodoc-skip-member', autodoc_skip_member)
#-----------------------------------------------------------
from mock import Mock as MagicMock

class Mock(MagicMock):  
    @classmethod
    def __getattr__(cls, name):
            return MagicMock()

MOCK_MODULES = ['ete3', 'dendropy', 'dendropy.calculate.treecompare', 'itolapi', 'itolapi.Itol', 'itolapi.ItolExport', 'ete3.Tree', 'ete3.TreeStyle', 'ete3.parser.newick.NewickError']  
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)  
