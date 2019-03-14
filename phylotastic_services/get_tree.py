"""
**get_tree** Module is for getting a phylogenetic tree from a list of taxa
"""

import json
import time
import types
import urllib
import requests
import os
import re
import ast
import datetime
import tempfile
#----------------
#from itolapi import Itol
#from itolapi import ItolExport

from ete3 import Tree
from ete3.parser.newick import NewickError
from resolve_names import resolve_names_OT

#from requests.packages.urllib3.exceptions import InsecureRequestWarning
#Suppress warning for using a version of Requests which vendors urllib3 inside
#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
megatree_plants = ["R20120829", "smith2011", "zanne2014"]
megatree_mammals = ["binindaemonds2007"]

api_url = "https://api.opentreeoflife.org/v3/"
headers = {'content-type': 'application/json'}
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
#-----------------Induced Subtree of a set of nodes [OpenTree]---------------------
#input: list (comma separated) of ottids (long)   
#output: json object with inducedsubtree in newick key and status message in message key
def get_inducedSubtree(ottIdList):
    resource_url = api_url + "tree_of_life/induced_subtree"    
    
    payload_data = {
     	'ott_ids': ottIdList
    }
    jsonPayload = json.dumps(payload_data)
    
    response = requests.post(resource_url, data=jsonPayload, headers=headers)
    
    newick_tree_str = ""
    studies = ""
    inducedtree_info = {}

    if response.status_code == requests.codes.ok:
 		data_json = json.loads(response.text)
 		newick_tree_str = data_json['newick']
 		studies = data_json['supporting_studies']		
 		inducedtree_info['message'] = "Success"
 		inducedtree_info['status_code'] = 200
    else:
 		try: 
 			error_msg = str(response.text)
 			if 'node_id' in error_msg:
 				st_indx = error_msg.find("node_id")  #"[/v3/tree_of_life/induced_subtree] Error: node_id 'ott4284156' was not found!"
 				en_indx = error_msg.find("was")
 				missing_node_id_str = error_msg[st_indx+9: en_indx-2]
 				missing_ott_id = int(missing_node_id_str.replace("ott", ""))
 				ottIdList.remove(missing_ott_id)
 				return ottIdList
 			else:
 				error_json = json.loads(error_msg)
 				error_msg = error_json['message']
 		 		inducedtree_info['message'] = "OpenTreeofLife API Error: " + error_msg
         	
 		except Exception as e:
 			inducedtree_info['message'] =  "OpenTreeofLife API Error: " + str(e)
     		 	
    inducedtree_info['status_code'] = response.status_code

    inducedtree_info['newick'] = newick_tree_str
    inducedtree_info['studies'] = studies
 	
    return inducedtree_info

#-------------------------------------------------------
def subtree(ottidList):
    induced_response = get_inducedSubtree(ottidList)
    while type(induced_response) == types.ListType: 
        induced_response = get_inducedSubtree(induced_response)    
 
    return induced_response 

#-----------------------------------------------------------
#get newick string for tree from OpenTree
#input: list of resolved scientific names
#get newick string for tree from OpenTree
#input: list of resolved scientific names
def get_tree_OT(resolvedNames, include_metadata=False, include_ottid=True):
 	start_time = time.time() 
 	ListSize = len(resolvedNames)
    
 	response = {}
 	if ListSize == 0:
 		response['newick'] = ""
 		response['message'] = "Error: List of resolved names empty"
 		response['status_code'] = 500
 		
 		return response
 		
 	rsnames = resolvedNames
 	#rsnames = resolvedNames['resolvedNames']
 	ottIdList = []
 	for rname in rsnames:
 		if 'matched_results' in rname:
 			for match_result in rname['matched_results']:
 				if 'Open Tree of Life' in match_result['data_source']:
 					ottIdList.append(match_result['taxon_id'])
 					break 			
 		else:
 			if rname['resolver_name'] == 'OT':
 				ottIdList.append(rname['taxon_id'])
 			else:
 				response['newick'] = ""
 				response['message'] = "Error: wrong TNRS. Need to resolve with OpenTreeofLife TNRS"
 				response['status_code'] = 500
 			 	return response
 			     
    #get induced_subtree
 	final_result = {} 
 	opentree_result = subtree(ottIdList)
 	newick_str = opentree_result['newick']
 	if newick_str.find(";") == -1:
 		newick_str = newick_str + ";"

 	if not(include_ottid):
 		# Delete ott_ids from tip_labels
 		nw_str = newick_str
 		nw_str = re.sub('_ott\d+', "", nw_str)
 		newick_str = nw_str.replace('_', " ")
   
 	final_result['newick'] = newick_str#newick_str.encode('ascii', 'ignore').decode('ascii')
 	if opentree_result['status_code'] != 200:	
 		return opentree_result 
 
 	if opentree_result['newick'] != "":
 		final_result['message'] = "Success"
 		final_result['status_code'] = 200

 		if include_metadata:
 			synth_tree_version = get_tree_version()		
 			tree_metadata = get_metadata()
 			tree_metadata['inference_method'] = tree_metadata['inference_method'] + " from synthetic tree with ID "+ synth_tree_version
 			final_result['tree_metadata'] = tree_metadata
 			final_result['tree_metadata']['synthetic_tree_id'] = synth_tree_version
 			#https://wiki.python.org/moin/UnicodeDecodeError
 			newick_str = newick_str.encode('utf-8', 'ignore')
 			num_tips = get_num_tips(newick_str)
 			if num_tips != -1:
 				final_result['tree_metadata']['num_tips'] = num_tips

 			study_ids = opentree_result['studies']
 			study_list = get_supporting_studies(study_ids) 	
 			final_result['tree_metadata']['supporting_studies'] = study_list
 		 
 	end_time = time.time()
 	execution_time = end_time-start_time
    #service result creation time
 	creation_time = datetime.datetime.now().isoformat()
 	meta_data = {}
 	meta_data['creation_time'] = creation_time
 	meta_data['execution_time'] = float("{:4.2f}".format(execution_time))
 	meta_data['source_urls'] = ["https://github.com/OpenTreeOfLife/opentree/wiki/Open-Tree-of-Life-APIs#tree_of_life"]

 	final_result['meta_data'] = meta_data  

 	return final_result

#--------------------------------------------
#------------------------(OpenTree-studies)------------------------------
def get_study_info(studyid):
    opentree_method_url = api_url + "studies/find_studies"
    
    payload = {
        'property': 'ot:studyId',
        'value': studyid,
        'verbose': True	
    }
    
    jsonPayload = json.dumps(payload)
    
    response = requests.post(opentree_method_url, data=jsonPayload, headers=headers)
    
    studyinfo_result = {}
    result_data_json = json.loads(response.text)

    if response.status_code == requests.codes.ok:    
        
        if (len(result_data_json['matched_studies']) == 0):
           studyinfo_result['message'] =  "No matching study found"
     	   studyinfo_result['status_code'] = 200
        else: 
           if ('ot:studyPublicationReference' in result_data_json['matched_studies'][0]):
              studyinfo_result['Publication'] = result_data_json['matched_studies'][0]['ot:studyPublicationReference']
           else:
              studyinfo_result['Publication'] = ""
           if ('ot:studyId' in result_data_json['matched_studies'][0]):
              studyinfo_result['PublicationIdentifier'] = result_data_json['matched_studies'][0]['ot:studyId']
           else:
              studyinfo_result['PublicationIdentifier'] = studyid
           if ('ot:curatorName' in result_data_json['matched_studies'][0]):
              studyinfo_result['Curator'] = result_data_json['matched_studies'][0]['ot:curatorName']
           else:
              studyinfo_result['Curator'] = ""
           if ('ot:studyYear' in result_data_json['matched_studies'][0]):
              studyinfo_result['PublicationYear'] = result_data_json['matched_studies'][0]['ot:studyYear']
           else:
              studyinfo_result['PublicationYear'] = ""
           if ('ot:focalCladeOTTTaxonName' in result_data_json['matched_studies'][0]):
              studyinfo_result['FocalCladeTaxonName'] = result_data_json['matched_studies'][0]['ot:focalCladeOTTTaxonName']
           else:
              studyinfo_result['FocalCladeTaxonName'] = ""
           if ('ot:studyPublication' in result_data_json['matched_studies'][0]):
              studyinfo_result['PublicationDOI'] = result_data_json['matched_studies'][0]['ot:studyPublication']
           else:
              studyinfo_result['PublicationDOI'] = ""
           if ('ot:dataDeposit' in result_data_json['matched_studies'][0]):
              studyinfo_result['DataRepository'] = result_data_json['matched_studies'][0]['ot:dataDeposit']
           else:
              studyinfo_result['DataRepository'] = ""
           if ('ot:candidateTreeForSynthesis' in result_data_json['matched_studies'][0]):
              studyinfo_result['CandidateTreeForSynthesis'] = result_data_json['matched_studies'][0]['ot:candidateTreeForSynthesis']
           else:
              studyinfo_result['CandidateTreeForSynthesis'] = ""
        
        studyinfo_result['message'] =  "Success"
     	studyinfo_result['status_code'] = 200
    else:    
        if 'message' in result_data_json:
           studyinfo_result['message'] = "OpenTree Error: "+result_data_json['message']
        else:
           studyinfo_result['message'] = "Error: Response error while getting study info from OpenTreeofLife"
        
        studyinfo_result['status_code'] = response.status_code
        
    #print studyinfo_result
    return studyinfo_result

#-----------------------------------------
#get supporting studies of the tree from OpenTree
def get_supporting_studies(studyid_list):
    studies_list = []
    study_ids = [study[:study.find("@")] for study in studyid_list]
    for studyid in study_ids:
        study_info = get_study_info(studyid)
        if study_info['status_code'] == 200:
           msg = study_info['message']
           status = study_info['status_code']
           #delete status keys from dictionary 
           del study_info['status_code']
           del study_info['message']
           studies_list.append(study_info)
        else:
           msg = study_info['message']
           status = study_info['status_code']
           break    

    return studies_list

#--------------------------------------------
#find the number of tips in the tree
def get_num_tips(newick_str):
 	parse_error = False
 	try:
 		tree = Tree(newick_str)
 	except NewickError:
 		try:
 			tree = Tree(newick_str, format=1)
 		except NewickError as e:
 			#print str(e) 
 			if 'quoted_node_names' in str(e):
 				try:
 					tree = Tree(newick_str, format=1, quoted_node_names=True)
 				except NewickError as e:
 					parse_error = True	
 			else:
 				parse_error = True

 	if not(parse_error):
 		tips_list = [leaf for leaf in tree.iter_leaves()]            
 		tips_num = len(tips_list)
 	else:
 		tips_num = -1

 	return tips_num

#-------------------------------------------
def get_tree_version():
 	resource_url = api_url + "tree_of_life/about"    
    
 	response = requests.post(resource_url)
 	        
 	metadata = {}
 	if response.status_code == requests.codes.ok:
 		data_json = json.loads(response.text)
 		return data_json['synth_id']
 	else:
 		return "" #Error: getting synth tree version"  

#---------------------------------------------
def get_metadata():
 	tree_metadata = {}
 	tree_metadata['topology_id'] = "NA"
 	tree_metadata['gene_or_species'] = "species"
 	tree_metadata['rooted'] = True
 	tree_metadata['anastomosing'] = False
 	tree_metadata['consensus_type'] = "NA"
 	tree_metadata['branch_lengths_type'] = None
 	tree_metadata['branch_support_type'] = None
 	tree_metadata['character_matrix'] = "NA"
 	tree_metadata['alignment_method'] = "NA"
 	tree_metadata['inference_method'] = "induced_subtree"

 	return tree_metadata
	
#--------------------------------------------
def get_tree_OpenTree(taxa, metadata = False, ottid = True):
 	"""Gets a phylogenetic tree from a list of taxa using Open Tree of Life APIs
    
	Example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.get_tree_OpenTree(taxa=["Setophaga striata","Setophaga magnolia","Setophaga angelae","Setophaga plumbea","Setophaga virens"])
	>>> print result
	{"status_code": 200, "message": "Success", "meta_data": {"execution_time": 2.46, "creation_time": "2019-03-13T16:56:32.243413", "source_urls": ["https://github.com/OpenTreeOfLife/opentree/wiki/Open-Tree-of-Life-APIs#tree_of_life"]}, "tree_metadata": {"alignment_method": "NA", "character_matrix": "NA", "rooted": true, "supporting_studies": [{"PublicationYear": 2015, "FocalCladeTaxonName": "Aves", "Publication": "Burleigh, J. Gordon, Rebecca T. Kimball, Edward L. Braun. 2015. Building the avian tree of life using a large-scale, sparse supermatrix. Molecular Phylogenetics and Evolution 84: 53-63", "CandidateTreeForSynthesis": "tree1", "PublicationDOI": "http://dx.doi.org/10.1016/j.ympev.2014.12.003", "DataRepository": "http://dx.doi.org/10.5061/dryad.r6b87", "Curator": "Joseph W. Brown", "PublicationIdentifier": "ot_521"}, {"PublicationYear": 2012, "FocalCladeTaxonName": "Aves", "Publication": "Jetz, W., G. H. Thomas, J. B. Joy, K. Hartmann, A. O. Mooers. 2012. The global diversity of birds in space and time. Nature 491 (7424): 444-448", "CandidateTreeForSynthesis": "tree2", "PublicationDOI": "http://dx.doi.org/10.1038/nature11631", "DataRepository": "", "Curator": "Joseph W. Brown", "PublicationIdentifier": "ot_809"}, {"PublicationYear": 2015, "FocalCladeTaxonName": "Passeriformes", "Publication": "Barker, F. Keith, Kevin J. Burns, John Klicka, Scott M. Lanyon, Irby J. Lovette. 2015. New insights into New World biogeography: An integrated view from the phylogeny of blackbirds, cardinals, sparrows, tanagers, warblers, and allies. The Auk 132 (2): 333-348.", "CandidateTreeForSynthesis": "tree1", "PublicationDOI": "http://dx.doi.org/10.1642/auk-14-110.1", "DataRepository": "http://datadryad.org/resource/doi:10.5061/dryad.pb787", "Curator": "Joseph W. Brown", "PublicationIdentifier": "ot_770"}, {"PublicationYear": 2010, "FocalCladeTaxonName": "Parulidae", "Publication": "Lovette, Irby J., Jorge L. P\u00e9rez-Em\u00e1n, John P. Sullivan, Richard C. Banks, Isabella Fiorentino, Sergio C\u00f3rdoba-C\u00f3rdoba, Mar\u00eda Echeverry-Galvis, F. Keith Barker, Kevin J. Burns, John Klicka, Scott M. Lanyon, Eldredge Bermingham. 2010. A comprehensive multilocus phylogeny for the wood-warblers and a revised classification of the Parulidae (Aves). Molecular Phylogenetics and Evolution 57 (2): 753-770.", "CandidateTreeForSynthesis": "tree6024", "PublicationDOI": "http://dx.doi.org/10.1016/j.ympev.2010.07.018", "DataRepository": "", "Curator": "Joseph W. Brown", "PublicationIdentifier": "pg_2591"}], "anastomosing": false, "branch_lengths_type": null, "consensus_type": "NA", "inference_method": "induced_subtree from synthetic tree with ID opentree10.4", "branch_support_type": null, "num_tips": 5, "gene_or_species": "species", "topology_id": "NA", "synthetic_tree_id": "opentree10.4"}, "newick": "((((Setophaga_striata_ott60236)mrcaott22834ott60236)mrcaott22834ott455853)mrcaott22834ott285200,Setophaga_plumbea_ott45750,Setophaga_angelae_ott381849,Setophaga_magnolia_ott532751,Setophaga_virens_ott1014098)Setophaga_ott285198;"}

    :param taxa: A list of taxa to be used to get a phylogenetic tree. 
    :type taxa: A list of strings. 
    :param metadata: A boolean value to specify whether to return metadata for tree. By default it is ``False``. If metadata is turned on, then it will return relevant metadata for the tree.
    :type metadata: boolean.
    :param ottid: A boolean value to specify whether to keep the ott ids of taxa in tree. By default it is ``True``. 
    :type ottid: boolean. 

    :returns: A json formatted string -- with a phylogenetic tree in newick format as the value of the ``newick`` property. 

    """
 	
 	nameslist_json = json.loads(resolve_names_OT(taxa))	
 	nameslist = nameslist_json["resolvedNames"]
 	service_result = get_tree_OT(nameslist, metadata, ottid)
   
 	return json.dumps(service_result)

#-------------------------------------------

#=======================================================
#get a tree using phylomatic
def get_phylomatic_tree(megatree_id, taxa):
 	api_url = "http://phylodiversity.net/phylomatic/pmws"    

 	payload = {
 		'storedtree': megatree_id,
 		'informat': "newick",
 		'method': "phylomatic",
 		'taxaformat' : "slashpath",
 		'outformat': "newick",
 		'clean': "true",
 		'taxa': taxa       
	}
 	encoded_payload = urllib.urlencode(payload)
 
 	response = requests.post(api_url, data=encoded_payload) 
  	
 	phylomatic_response = {}
 	
 	if response.status_code == requests.codes.ok:
 		phylomatic_response['response'] = response.text
 		phylomatic_response['status_code'] = 200
 		phylomatic_response['message'] = "Success"
 	else:
 		phylomatic_response['response'] = None
 		phylomatic_response['status_code'] = response.status_code
 		phylomatic_response['message'] = "Error: Response error while getting tree from phylomatic"

 	return phylomatic_response

#--------------------------------------------------------
#infer the taxonomic context from a list of taxonomic names 
def get_taxa_context(taxaList):
 	resource_url = api_url+"tnrs/infer_context"    
    
 	payload_data = {
     	'names': taxaList
    }

 	jsonPayload = json.dumps(payload_data)
 
 	response = requests.post(resource_url, data=jsonPayload, headers=headers)
 	    	
 	if response.status_code == requests.codes.ok:
 		json_response = json.loads(response.text)
 		context = json_response['context_name']
 	else:
 		context = None

 	return context

#-----------------------------------------------
#get a list of pre-defined taxonomic contexts from OpenTree
def get_contexts():
 	resource_url = api_url+"tnrs/contexts"    
    
 	response = requests.post(resource_url, headers=headers)
 	
 	if response.status_code == requests.codes.ok:
 		return response.text
 	else:
 		return None

#---------------------------------------------
def process_taxa_list(taxaList):
 	taxa = "\n".join(taxaList)
 	taxa = taxa.replace(" ", "_")

 	return taxa

#---------------------------------------------
def process_phylomatic_result(result):
 	#print result
 	st_indx = result.find("[")
 	#print "St indx:" + str(st_indx)
 	en_indx = result.find("]")
 	#print "En indx:" + str(en_indx)
 	extra_note = result[st_indx : en_indx+1]
 	#print extra_note
 	newick_str = result[0: st_indx]
 	if st_indx != -1 and en_indx != -1:
 		newick_str += ";"
 	#print newick_str
 	#newick_str = newick_str.replace("_", " ")
 	#print newick_str

 	return {"newick": newick_str, "note": extra_note}

#---------------------------------------------
#get tree using phylomatic
def get_tree_phyloMT(taxaList, post=False):
 	start_time = time.time()	
 	 	
 	context = get_taxa_context(taxaList)
 	if context is not None:
 		contexts = json.loads(get_contexts())	
 		for cname, clist in contexts.items():
 			if context in clist:
 				context_name = cname
 				break
 		context_l = context_name.lower()
	else:
		context_l = ""

 	#find megatree corresponding to this list	
 	if  context_l == "animals":
 		megatree_list = megatree_mammals
 	elif context_l == "plants":
 		megatree_list = megatree_plants
 	else:
 		megatree_list = None

 	taxa = process_taxa_list(taxaList)

 	final_result = {}

 	if megatree_list is None: #try all megatrees
 		megatree_list = megatree_mammals + megatree_plants

 	for megatree_id in megatree_list:
 		phylomatic_result = get_phylomatic_tree(megatree_id, taxa)
 		if phylomatic_result['response'] is None:
 			final_result = {"newick": "", "status_code": phylomatic_result['status_code'], "message": phylomatic_result['message']}
 			break
 		else:
 			if "No taxa in common" in phylomatic_result['response']:
 				continue
 			else:			
 				processed_result = process_phylomatic_result(phylomatic_result['response'])
 				final_result = {"newick": processed_result['newick'], "status_code": 200, "message": "Success"}
 				break

 	if not(final_result):
 		final_result = {"newick": "", "status_code": 200, "message": "No tree found using phylomatic web service"}

 	end_time = time.time()
 	execution_time = end_time-start_time
    #service result creation time
 	creation_time = datetime.datetime.now().isoformat()
 	source_urls = ["http://phylodiversity.net/phylomatic/"]
 	
	meta_data = {'creation_time': creation_time, 'execution_time': float("{:4.2f}".format(execution_time)), 'source_urls': source_urls}
 	final_result['meta_data'] = meta_data 
 	final_result['input_taxa'] = taxaList 	 

 	return final_result    
 
#---------------------------------------------
def get_tree_Phylomatic(taxa):
 	"""Gets a phylogenetic tree from a list of taxa using Phylomatic API
    
	Example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.get_tree_Phylomatic(taxa=["Annona cherimola", "Annona muricata", "Quercus robur", "Shorea parvifolia"])
	>>> print result
	{"execution_time": "4.54", "status_code": 200, "message": "Success", "creation_time": "2017-07-02T12:27:53.990405", "newick": "(Annona_muricata,(Quercus_robur,Shorea_parvifolia));"}

    :param taxa: A list of taxa to be used to get a phylogenetic tree. 
    :type taxa: A list of strings.  
    :returns: A json formatted string -- with a phylogenetic tree in newick format as the value of the ``newick`` property. 

    """
	service_result = get_tree_phyloMT(taxa)

	return json.dumps(service_result)

#======================================================
'''
#get ncbi id available for a taxon
def find_taxon_id(taxonName):
 	api_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"	  
 	payload = {
 		'retmax': 1000,
 		'retmode': 'json',
 		'db': 'taxonomy',
 		'term': taxonName,
 		'tool': "phylotastic-services",
 		'email': "tayeen@nmsu.edu"      
    }
 	encoded_payload = urllib.urlencode(payload)
 	response = requests.get(api_url, params=encoded_payload)#, headers={'content-type': 'application/json'}) 
 	
 	ncbi_id_list = []	
 	ncbi_response = {}    
 	ncbi_response['status_code'] = 200
 	ncbi_response['message'] = "Success"
 	
 	numResults = 0
 
 	if response.status_code == requests.codes.ok:    
 		data_json = json.loads(response.text)
 		numResults = int(data_json['esearchresult']['count']) 
 		if numResults > 0:
 			ncbi_id_list = data_json['esearchresult']['idlist']  
 	else: 
 		ncbi_response['status_code'] = response.status_code
 		ncbi_response['message'] = "Error: Response error from NCBI esearch.fcgi API"

	ncbi_response['taxon_ids'] = ncbi_id_list
 	
 	if numResults == 0 and ncbi_response['status_code'] == 200:
  	 	ncbi_response['message'] = "No match found for term '%s'" %(taxonName)
 	
 	return ncbi_response 	
'''
#---------------------------------------------------------
'''
#get a tree using phyloT
def get_tree_itol(tempDir, ncbiIdDict):
 	
 	phyloT_temp_path = tempDir	

 	#-----Create the Itol class------
 	itol_uploader = Itol.Itol()
 	#-----Add parameters-------
 	# parameter name: "ncbiFile"
	# parameter description: instead of uploading a tree, iTOL can automatically generate one from a file containing a list of NCBI tax IDs. NCBI taxonomy will be pruned based on your IDs and a Newick tree generated. Input file location

 	itol_uploader.add_variable('ncbiFile', os.path.join(phyloT_temp_path, "ids.txt"))

 	# parameter name: "ncbiFormat"
 	# parameter description: format of the tree generated using NCBI tax IDs:
 	#			'namesFull': generated tree will contain scientific names and internal nodes will not be collapsed
 	#			'namesCollapsed': scientific names will be used, and internal nodes with only one child removed
 	# 			'idsFull': tree will contain NCBI taxonomy IDs and internal nodes will not be collapsed
 	# 			'idsCollapsed': NCBI taxonomy IDs will be used, and internal nodes with only one child remove

 	itol_uploader.add_variable('ncbiFormat', 'idsFull')

 	# parameter name: "treeName"
 	# parameter description: name of the tree generated using NCBI tax IDs:

 	itol_uploader.add_variable('treeName', 'phylotree')

 	upload_status = itol_uploader.upload()

 	if not upload_status:
 		return {"message": "There was an error:" + itol_uploader.comm.upload_output, "status_code": 500}
 	else:    
 		# Read the iTOL API return statement
 		upload_output = str(itol_uploader.comm.upload_output)
 		if upload_output.find("SUCCESS") == -1: # SUCCESS: 174561252042902514884188540
 			return {"message": "No tree found in phyloT" , "status_code": 204}

 	# Read the tree ID
 	tree_id = str(itol_uploader.comm.tree_id) #Tree ID: 174561252042902514884188540

 	# Export the tree above to newick
 	#print('Exporting tree to newick')
 	itol_exporter = itol_uploader.get_itol_export()

 	export_location = os.path.join(phyloT_temp_path, "output_phylot.txt")
 	#print export_location
 	if os.path.exists(export_location):
 		#print "Removing output file"
 		os.remove(export_location)	

 	itol_exporter.set_export_param_value('format', 'newick')
 	itol_exporter.export(export_location)
 	#print('exported tree to ', export_location)
 	
 	output_file = open(export_location, "r")
 	newick_str = output_file.read()
 	#process phyloT result
 	for ncbi_id, taxon in ncbiIdDict.items():	
 		newick_str = newick_str.replace(ncbi_id, taxon)
 	
 	newick_str = newick_str.replace("\n", "")
 	newick_str = re.sub(r'[\:\.0-9]', "", newick_str)
 	final_newick_str = newick_str.replace(" ", "_")
 
 	output_file.close()
	#remove temporary files and directories
 	#print "Removing temp ..."
 	os.remove(os.path.join(phyloT_temp_path, "ids.txt"))
 	os.remove(os.path.join(phyloT_temp_path, "output_phylot.txt"))

 	if os.path.exists(phyloT_temp_path):
 		os.rmdir(phyloT_temp_path)
	
 	return {"newick": final_newick_str, "message": "Success", "status_code": 200}

#-----------------------------------------------
#create a dictionary of ncbi ids from a taxa list
def get_ncbi_ids(taxaList):
 	ncbi_id_dic = {}
 	for taxon_name in taxaList:
 		taxon_result = find_taxon_id(taxon_name)
 		if taxon_result['status_code'] == 200:
 			ncbi_id_taxon = taxon_result['taxon_ids'][0]
 			ncbi_id_dic[ncbi_id_taxon] = taxon_name

 	return ncbi_id_dic		

#---------------------------------------------
#create a input file with ncbi ids
def create_file_input_ids(ncbiIdDict):
 	
 	#make a temporary directory
 	tmpdir = tempfile.mkdtemp()	
 	
 	file_path = os.path.join(tmpdir, "ids.txt")
 	print file_path
 	try:
 		with open(file_path, "w") as tmp:
 			counter = 0
 			dictLen = len(ncbiIdDict)
 			for ncbi_id, taxon in ncbiIdDict.items():
 				tmp.write(ncbi_id)
 				counter += 1
 				if counter != dictLen:
 					tmp.write("\n")
 	except IOError as e:
 		print 'IOError'
 			
 	return tmpdir
'''
#---------------------------------------------
'''
def get_tree_phyloT(taxaList, post=False):
 	
 	start_time = time.time()
 	 	
 	NCBI_dict = get_ncbi_ids(taxaList)
 	temp_file_dir = create_file_input_ids(NCBI_dict)
	get_tree_response = get_tree_itol(temp_file_dir, NCBI_dict)
 	
 	final_result = {}
 	if get_tree_response['status_code'] == 200:
 		final_result['tree_newick'] = get_tree_response['newick']
	else:
 		final_result['tree_newick'] = ""
 			
 	final_result['status_code'] = get_tree_response['status_code']
 	final_result['message'] = get_tree_response['message']	
 		
 	end_time = time.time()
 	execution_time = end_time-start_time
    #service result creation time
 	creation_time = datetime.datetime.now().isoformat()
 	final_result['creation_time'] = creation_time
 	final_result['execution_time'] = "{:4.2f}".format(execution_time)
 	final_result['query_taxa'] = taxaList		

 	return final_result
''' 	
#-------------------------------------------
'''
def get_tree_NCBI(taxa):
 	"""Gets a phylogenetic tree from a list of taxa based on NCBI taxonomy using PhyloT
    
	Example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.get_tree_NCBI(taxa=["Panthera uncia", "Panthera onca", "Panthera leo", "Panthera pardus"])
	>>> print result
	{"execution_time": "7.86", "status_code": 200, "creation_time": "2017-07-02T15:55:16.470304", "query_taxa": ["Panthera uncia", "Panthera onca", "Panthera leo", "Panthera pardus"], "tree_newick": "(Panthera_pardus,Panthera_onca,Panthera_uncia,Panthera_leo);", "message": "Success", "service_documentation": "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-19"}

    :param taxa: A list of taxa to be used to get a phylogenetic tree. 
    :type taxa: A list of strings.  
    :returns: A json formatted string -- with a phylogenetic tree in newick format as the value of the ``tree_newick`` property. 

    """
	service_result = get_tree_phyloT(taxa)

	return service_result
'''

#---------------------------------------------
#if __name__ == '__main__':

#    result = get_tree_OpenTree(["Setophaga striata","Setophaga magnolia","Setophaga angelae","Setophaga plumbea","Setophaga virens"])
    #result = get_tree_NCBI(taxa=["Panthera uncia", "Panthera onca", "Panthera leo", "Panthera pardus"])
#    print result
    
       
