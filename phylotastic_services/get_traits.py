"""
**get_traits** Module is for getting traits (habitat and conservation status) about species 
"""
import json
import requests
import time
import datetime 
from os.path import dirname, abspath
import ConfigParser
import xml.etree.ElementTree as ET

#----------------------------------------------
headers = {'content-type': 'application/json'}
base_url = "http://eol.org/api/"
#-----------------------------------------
def get_api_key():
	config = ConfigParser.ConfigParser()
	current_dir = dirname(abspath(__file__))
	#config.read(current_dir + "/"+ "service.cfg")
	config.read(current_dir + "/"+ "config.py")

	api_key = config.get('EOL', 'api_key')

	return api_key

#----------------------------------------------
#----------------------------------------------
def match_species(species_name):
	EOL_API_Key = get_api_key()

	search_url = base_url+"search/1.0.json"    
	payload = {
 		'key': EOL_API_Key,
 		'q': species_name,
 		'page': 1,
 		'exact': True,
 		'filter_by_taxon_concept_id': "",
 		'filter_by_hierarchy_entry_id': "",
 		'filter_by_string': "", 
 		'cache_ttl': ""
    }
 	
	#encoded_payload = urllib.urlencode(payload)
	response = requests.get(search_url, params=payload) 

	match_result = {}     
 	if response.status_code == requests.codes.ok:    
		data_json = json.loads(response.text) 
		numResults = data_json['totalResults']
		if numResults != 0:
			match_result['matched_name'] = data_json['results'][0]['title']
			match_result['eol_id'] = data_json['results'][0]['id']
		else:
			match_result['matched_name'] = ""
			match_result['eol_id'] = ""
	else:	 	
 		match_result = None
 	 
 	return match_result

#----------------------------------------------------
def get_traits(species_eol_id):
	traits_url = base_url+ "traits/" + str(species_eol_id)   
	
	response = requests.get(traits_url) 

	trait_result = {}
	habitats_set = set()
	conservation_status = None
     
 	if response.status_code == requests.codes.ok:    
		data_json = json.loads(response.text) 
		trait_result['matched_species'] = data_json['item']['scientificName']
		traits_list = data_json['item']['traits']
		for trait in traits_list:
			if trait['predicate'] == "habitat":
				habitats_set.add(trait['value'])
			elif trait['predicate'] == "conservation status":		
				conservation_status = trait['value']

		trait_result['habitats'] = list(habitats_set)
		trait_result['conservation_status'] = conservation_status	
	else:	 	
 		trait_result = None
 	 
 	return trait_result


#---------------------------------------------------
def get_traits_EOL(inputSpeciesList):
	"""Gets habitat and conservation status of a list of species from EOL traitsbank
    
	**Note**> maximum ``30`` species allowed as input. 

	
	Example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.get_traits_EOL(["Balaenoptera musculus"])
	>>> print result
	{"status_code": 200, "message": "Success", "meta_data": {"execution_time": 0.65, "creation_time": "2018-06-10T17:01:10.884018", "source_urls": ["http://eol.org/traitbank"]}, "species": [{"habitats": ["temperate", "tropical", "blowhole", "pelagic zone", "oceanic zone", "continental shelf", "saline water", "marine habitat", "aquatic habitat", "strait", "ocean", "coast", "peninsula", "plateau", "sea", "island", "marine biome", "ridge", "bay"], "searched_name": "Balaenoptera musculus", "conservation_status": "endangered", "eol_id": 328574, "matched_name": "Balaenoptera musculus (Linnaeus, 1758)"}]}

    :param inputSpeciesList: A list of species for which to get habitat and conservation status. 
    :type inputSpeciesList: A list of strings.  

    :returns: A json formatted string -- with habitat and conservation status of each species. 

    """
	start_time = time.time()

	response = {}	
	outputSpeciesList = []

	for inputSpecies in inputSpeciesList:
		species_obj = {}	 	
		match_species_result = match_species(inputSpecies)
		species_obj['searched_name'] = inputSpecies	 	
		if match_species_result is None:		 	
			species_obj['matched_name'] = ""		
		elif match_species_result['eol_id'] != "":
			species_habitat_info = get_traits(match_species_result['eol_id'])
			if species_habitat_info is not None:
				species_obj['eol_id'] = match_species_result['eol_id']
			 	species_obj['habitats'] = species_habitat_info['habitats']
				species_obj['conservation_status'] = species_habitat_info['conservation_status']
				species_obj['matched_name'] = species_habitat_info['matched_species']
			else:
				species_obj['habitats'] = []
				species_obj['matched_name'] = []
		else:
			species_obj['matched_name'] = "" 
 				
		outputSpeciesList.append(species_obj)	
 	
	end_time = time.time()
	execution_time = end_time-start_time
    #service result creation time
	creation_time = datetime.datetime.now().isoformat()
	meta_data = {'creation_time': creation_time, 'execution_time': float('{:4.2f}'.format(execution_time)), 'source_urls':["http://eol.org/traitbank"] }

	response['meta_data'] = meta_data
 	
	response['message'] = "Success"
	response['status_code'] = 200
	response['species'] = outputSpeciesList

	return json.dumps(response)

#====================================================
def get_traits_ECOS(inputSpeciesList):
	"""Gets conservation status of a list of species using ECOS services
    
	**Note**> maximum ``30`` species allowed as input. 
	
	Example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.get_traits_ECOS(["Loxodonta africana"])
	>>> print result
	{"status_code": 200, "message": "Success", "meta_data": {"execution_time": 0.52, "creation_time": "2018-06-10T17:04:03.211812", "source_urls": ["https://ecos.fws.gov/ecp/services"]}, "species": [{"searched_name": "Loxodonta africana", "tsn_id": "584939", "matched_name": "Loxodonta africana", "conservation_status": "Threatened"}]}

    :param inputSpeciesList: A list of species for which to get conservation status. 
    :type inputSpeciesList: A list of strings.  

    :returns: A json formatted string -- with conservation status of each species. 

    """
	start_time = time.time()

	response = {}	
	outputSpeciesList = []
	error_resp_list = []

	for inputSpecies in inputSpeciesList:
		species_obj = {}	 	
		match_species_result = search_species(inputSpecies)
		species_obj['searched_name'] = inputSpecies	 	
		if match_species_result is None:		 	
			error_resp_list.append(inputSpecies)		
		else:
			species_conservation_info = parse_xml(match_species_result)
			if species_conservation_info is not None:
				species_obj['tsn_id'] = species_conservation_info['tsn_id']
				species_obj['conservation_status'] = species_conservation_info['conservation_status']
				species_obj['matched_name'] = species_conservation_info['matched_name']
			else:
				species_obj['matched_name'] = "" 
 				
			outputSpeciesList.append(species_obj)	
 	
	end_time = time.time()
	execution_time = end_time-start_time
    #service result creation time
	creation_time = datetime.datetime.now().isoformat()
	meta_data = {'creation_time': creation_time, 'execution_time': float('{:4.2f}'.format(execution_time)), 'source_urls':["https://ecos.fws.gov/ecp/services"] }
	
	if len(error_resp_list) == len(inputSpeciesList):
		response['message'] = "Error while getting response from ECOS API"
		response['status_code'] = 500	
	else:
		response['meta_data'] = meta_data
 		response['message'] = "Success"
		response['status_code'] = 200
		response['species'] = outputSpeciesList

	return json.dumps(response)

#----------------------------------------------
#https://ecos.fws.gov/ecp0/TessQuery?request=query&xquery=/SPECIES_DETAIL[SCINAME=%22Panthera%20tigris%22]
def search_species(species_name):
	api_url = "https://ecos.fws.gov/ecp0/TessQuery"    
	payload = {
 		'request': "query",
 		'xquery': "/SPECIES_DETAIL[SCINAME="+'"'+species_name+'"]'
    }
 	
	response = requests.get(api_url, params=payload) 

	xml_result = None     
 	if response.status_code == requests.codes.ok:    
		xml_result = response.text
		
	return xml_result 

#----------------------------------------
def parse_xml(xml_str):
	root = ET.fromstring(xml_str)
	if len(root) == 0: #no match found
		return None
	#print root.tag
	detail = root.find('SPECIES_DETAIL')
	sc_name = detail.find('SCINAME').text
	conservaion_status = detail.find('STATUS_TEXT').text
	tsn_id = detail.find('TSN').text

	return {'matched_name': sc_name, 'tsn_id': tsn_id, 'conservation_status': conservaion_status}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#if __name__ == '__main__':

	#inputSpecies = ["Panthera leo", "Panthera onca"]
 	#inputSpecies = ["Rangifer tarandus"]
 	
 	
