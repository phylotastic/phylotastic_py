"""
Python library to access phylotastic services.
"""
from .extract_names import extract_names_URL
from .extract_names import extract_names_TEXT
from .resolve_names import resolve_names_OT
from .resolve_names import resolve_names_GNR
from .get_tree import get_tree_OpenTree
from .get_tree import get_tree_Phylomatic
from .get_tree import get_tree_NCBI
from .get_species import get_all_species
from .get_species import get_country_species
from .get_info import get_images_species
from .get_info import get_eolurls_species
from .study_tree import compare_trees
from .study_tree import get_studies_tree

