"""
**get_info** Module is for getting data (image urls, eol info links) about species 
"""
import json
import requests
import time
import datetime 
import urllib
from os.path import dirname, abspath
import ConfigParser
import config

#----------------------------------------------
headers = {'content-type': 'application/json'}

#-----------------------------------------
def get_api_key():
	#config = ConfigParser.ConfigParser()
	#current_dir = dirname(abspath(__file__))
	#config.read(current_dir + "/"+ "service.cfg")
	#config.read(current_dir + "/"+ "config.py")
	#api_key = config.get('EOL', 'api_key')
	API_KEY_CONFIG = config.API_KEY
	api_key = API_KEY_CONFIG.EOL

	return api_key

#----------------------------------------------
def match_species(speciesName):
 	search_url = "http://eol.org/api/search/1.0.json" 
 	EOL_API_Key = get_api_key()    
 	payload = {
 		'key': EOL_API_Key,
 		'q': speciesName,
 		'page': 1,
 		'exact': True,
 		'filter_by_taxon_concept_id': "",
 		'filter_by_hierarchy_entry_id': "",
 		'filter_by_string': "", 
 		'cache_ttl': ""
    }
 	encoded_payload = urllib.urlencode(payload)
 	response = requests.get(search_url, params=encoded_payload, headers=headers) 
    
 	if response.status_code == requests.codes.ok:    
 		data_json = json.loads(response.text)
 		#length = len(data_json['results']) 
 		numResults = data_json['totalResults']   
 	
 	if numResults == 0:
 		return None 
 	else: 
 		return data_json

#--------------------------------------------
def get_eolurls_species(inputSpecies):
 	"""Gets information urls of a list of species from EOL.
    
	**Note**> maximum ``50`` species allowed as input. 

	Example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.get_eolurls_species(["Panthera leo", "Panthera onca"])
	>>> print result
	{"status_code": 200, "message": "Success", "species": [{"species_info_link": "http://eol.org/328672?action=overview&controller=taxa", "searched_name": "Panthera leo", "eol_id": 328672, "matched_name": "Panthera leo (Linnaeus, 1758)"}, {"species_info_link": "http://eol.org/328606?action=overview&controller=taxa", "searched_name": "Panthera onca", "eol_id": 328606, "matched_name": "Panthera onca (Linnaeus, 1758)"}]}

    :param inputSpecies: A list of species for which to get EOL links. 
    :type inputTaxon: A list of strings.  
    :returns: A json formatted string -- with a list of species objects containing links to EOL. 

    """
 	post=False
 	response = {}	
 	outputSpeciesList = []

 	for inSpecies in inputSpecies:
 		species_obj = {}
 		url_species = []	 	
 		match_species_json = match_species(inSpecies)
 		species_obj['searched_name'] = inSpecies	 	
 		if match_species_json is None:		 	
 			species_obj['matched_name'] = ""
 		else: 	
 		 	species_info_link = match_species_json['results'][0]['link']
 			species_obj['matched_name'] = match_species_json['results'][0]['title']
 			species_obj['eol_id'] = match_species_json['results'][0]['id']			
 			species_obj['species_info_link'] = species_info_link 
 				
 		outputSpeciesList.append(species_obj)	
 	
 	response['message'] = "Success"
 	response['status_code'] = 200
 	response['species'] = outputSpeciesList

 	if post:
 		return response
 	else:
 	 	return json.dumps(response)


#--------------------------------------------   
def get_species_info(speciesId):
 	page_url = "http://eol.org/api/pages/1.0/" + str(speciesId) +".json" 
 	EOL_API_Key = get_api_key()     
 	payload = {
 		'key': EOL_API_Key,
 		'batch' : False,
 		'id': speciesId,
 		'images_per_page': 5,
 		'images_page': 1,
 		'videos_per_page': 0,
 		'videos_page': 0,
 		'sounds_per_page': 0,
 		'sounds_page': 0,
 		'maps_per_page': 0,
 		'maps_page': 0,
 		'texts_per_page': 0,
 		'texts_page': 0,
 		'iucn': True, #include the IUCN Red List status object
 		'subjects': "overview",  #'overview' to return the overview text (if exists)
 		'licenses': "all",
 		'details': True, #include all metadata for data objects
 		'common_names': False,
 		'synonyms': False,
 		'references': False,
 		'taxonomy': True,
 		'vetted': 2, # only trusted and unreviewed content will be returned (untrusted content will not be returned)
 		'cache_ttl': "", 
 		'language': "en"
    }
 	encoded_payload = urllib.urlencode(payload)
 	response = requests.get(page_url, params=encoded_payload, headers=headers) 
    
 	if response.status_code == requests.codes.ok:    
 		species_info_json = json.loads(response.text)
 		return species_info_json
 	else:
 		return None
 		
#--------------------------------------------
def get_imageObjects(dataObjectsInfo):
 	species_imageobj_list = []
 	for dt_obj in dataObjectsInfo:
 		if dt_obj['dataType'] == 'http://purl.org/dc/dcmitype/StillImage':
 			img_obj = create_image_obj(dt_obj)
 			species_imageobj_list.append(img_obj)

 	return species_imageobj_list

#----------------------------------------------
def create_image_obj(dataObject):
 	#print dataObject
 	image_obj = {}
 	image_obj['source'] = dataObject['source'] if 'source' in dataObject else None
 	image_obj['vettedStatus'] = dataObject['vettedStatus']
 	image_obj['dataRating'] = dataObject['dataRating']
 	image_obj['mediaURL'] = dataObject['mediaURL']
 	image_obj['eolMediaURL'] = dataObject['eolMediaURL']
 	image_obj['eolThumbnailURL'] = dataObject['eolThumbnailURL']
 	image_obj['license'] = dataObject['license']
 	if dataObject.has_key('rightsHolder'):
 		image_obj['rightsHolder'] = dataObject['rightsHolder']
 	else:
 		image_obj['rightsHolder'] = ""

 	return image_obj

#---------------------------------------------------
def get_images_species(inputSpecies):
 	"""Gets image urls and corresponding license information of a list of species from EOL
    
	**Note**> maximum ``30`` species allowed as input. 
	
	Example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.get_images_species(["Rangifer tarandus"])
	>>> print result
	{"execution_time": "2.51", "status_code": 200, "creation_time": "2017-07-02T22:42:48.209751", "input_query": ["Rangifer tarandus"], "source_urls": ["http://eol.org"], "message": "Success", "species": [{"images": [{"license": "http://creativecommons.org/licenses/publicdomain/", "mediaURL": "http://www.biolib.cz/IMG/GAL/21652.jpg", "eolMediaURL": "http://media.eol.org/content/2014/05/02/09/88803_orig.jpg", "rightsHolder": "Nickles, Jon", "vettedStatus": "Trusted", "source": "http://www.biolib.cz/en/image/id21652/", "eolThumbnailURL": "http://media.eol.org/content/2014/05/02/09/88803_98_68.jpg", "dataRating": 3.0}, {"license": "http://creativecommons.org/licenses/by-nc-sa/3.0/", "mediaURL": "http://calphotos.berkeley.edu/imgs/256x384/6666_6666/1007/6477.jpeg", "eolMediaURL": "http://media.eol.org/content/2011/08/07/07/12395_orig.jpg", "rightsHolder": "2007 California Academy of Sciences", "vettedStatus": "Trusted", "source": "http://calphotos.berkeley.edu/cgi/img_query?seq_num=27882&one=T", "eolThumbnailURL": "http://media.eol.org/content/2011/08/07/07/12395_98_68.jpg", "dataRating": 4.0}, {"license": "http://creativecommons.org/publicdomain/mark/1.0/", "mediaURL": "http://upload.wikimedia.org/wikipedia/commons/f/fd/Caribou.jpg", "eolMediaURL": "http://media.eol.org/content/2013/06/18/06/80894_orig.jpg", "rightsHolder": "", "vettedStatus": "Trusted", "source": "http://commons.wikimedia.org/wiki/File:Caribou.jpg", "eolThumbnailURL": "http://media.eol.org/content/2013/06/18/06/80894_98_68.jpg", "dataRating": 3.45455}, {"license": "http://creativecommons.org/licenses/by-nc/2.0/", "mediaURL": "https://farm1.staticflickr.com/31/56038869_7421be89f6_o.jpg", "eolMediaURL": "http://media.eol.org/content/2015/01/12/03/89244_orig.jpg", "rightsHolder": "Caleb Slemmons", "vettedStatus": "Trusted", "source": "https://www.flickr.com/photos/kenai/56038869/", "eolThumbnailURL": "http://media.eol.org/content/2015/01/12/03/89244_98_68.jpg", "dataRating": 3.0}, {"license": "http://creativecommons.org/licenses/by-sa/3.0/", "mediaURL": "http://upload.wikimedia.org/wikipedia/commons/a/af/20070818-0001-strolling_reindeer.jpg", "eolMediaURL": "http://media.eol.org/content/2012/06/13/00/48543_orig.jpg", "rightsHolder": "", "vettedStatus": "Trusted", "source": "http://commons.wikimedia.org/wiki/File:20070818-0001-strolling_reindeer.jpg", "eolThumbnailURL": "http://media.eol.org/content/2012/06/13/00/48543_98_68.jpg", "dataRating": 3.0}], "searched_name": "Rangifer tarandus", "total_images": 5, "eol_id": 328653, "matched_name": "Rangifer tarandus (Linnaeus, 1758)"}]}



    :param inputSpecies: A list of species for which to get image url information. 
    :type inputTaxon: A list of strings.  
    :returns: A json formatted string -- with a list of species objects containing image urls, license info., eol ids. 

    """
 	start_time = time.time()
 	#service_url = "http://phylo.cs.nmsu.edu:5004/phylotastic_ws/si/eol/get_images?species=" + inputSpeciesList
 	#service_documentation = "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-8"
 	response = {}	
 	outputSpeciesList = []

 	for inSpecies in inputSpecies:
 		species_obj = {}
 		images_species = []	 	
 		match_species_json = match_species(inSpecies)
 		if match_species_json is None:
 			species_id = -1
 		else:
 			species_id = match_species_json['results'][0]['id']
 		species_obj['searched_name'] = inSpecies	 	
 		if species_id == -1:		 	
 			species_obj['matched_name'] = ""
 			species_obj['total_images'] = 0
 		else: 	
 		 	species_info_json = get_species_info(species_id)
 			if species_info_json is not None:
 				species_obj['matched_name'] = species_info_json[str(species_id)]['scientificName']
 				species_obj['eol_id'] = species_id			
 				try:			
 					dataObjects_lst = species_info_json[str(species_id)]['dataObjects']
 					length = len(dataObjects_lst)		
 					if length != 0:
 						images_species = get_imageObjects(dataObjects_lst)
 				except KeyError as e:
 					images_species = []
 		species_obj['total_images'] = len(images_species)
 		species_obj['images'] = images_species
 		outputSpeciesList.append(species_obj)
	
 	end_time = time.time()
 	execution_time = end_time-start_time    
    #service result creation time
 	creation_time = datetime.datetime.now().isoformat()
 	
 	response['creation_time'] = creation_time
 	response['execution_time'] = "{:4.2f}".format(execution_time)
 	response['message'] = "Success"
 	response['status_code'] = 200
 	response['species'] = outputSpeciesList
 	response['source_urls'] = ["http://eol.org"]
 	response['input_query'] = inputSpecies

 	return json.dumps(response)

#--------------------------------------------------
def get_image_species_id(species_id, post=False):
 	response = {}	
 	species_obj = {}
 	species_info_json = get_species_info(species_id)
 	if species_info_json is not None:
 		species_obj['matched_name'] = species_info_json['scientificName']
 		species_obj['eol_id'] = species_id			
 		dataObjects_lst = species_info_json['dataObjects'] 
 		length = len(dataObjects_lst)		
 		if length != 0:
 			images_species = get_imageObjects(dataObjects_lst)
 					
 		species_obj['images'] = images_species
 		
 	response['message'] = "Success"
 	response['status_code'] = 200
 	response['species'] = species_obj

 	if post:
 		return response
 	else:
 	 	return json.dumps(response)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#if __name__ == '__main__':

	#inputSpecies = ["Panthera leo", "Panthera onca"]
 	#inputSpecies = ["Rangifer tarandus"]
 	
 	#print get_images_species(inputSpecies)
 	#print get_eolurls_species(inputSpecies)
 	
