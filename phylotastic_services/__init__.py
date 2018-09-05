"""
Python library to access phylotastic services.
"""
from .extract_names import extract_names_URL
from .extract_names import extract_names_TEXT
from .resolve_names import resolve_names_OT
from .resolve_names import resolve_names_GNR
from .resolve_names import resolve_names_iPlant
from .get_tree import get_tree_OpenTree
from .get_tree import get_tree_Phylomatic
#from .get_tree import get_tree_NCBI
from .get_species import get_all_species
from .get_species import get_country_species
from .get_species import get_genome_species
from .get_info import get_images_species
from .get_info import get_eolurls_species
from .common_names import get_scientific_names
from .get_traits import get_traits_ECOS
from .get_traits import get_traits_EOL
from .study_tree import compare_trees
from .study_tree import get_chronogram_tree
from .list_species import List
from .list_species import Species
from .list_species import insert_list_info
from .list_species import update_list_metadata
from .list_species import update_list_data
from .list_species import get_list_info
from .list_species import remove_list_info

