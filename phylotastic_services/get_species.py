"""
**get_species** Module for getting species names belonging to an input taxon 
"""
#taxon to species service
import json
import requests
import urllib
import time
import datetime 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Open Tree of Life API
base_url = "http://phylo.cs.nmsu.edu:5004/phylotastic_ws/ts/"
api_url = "https://api.opentreeoflife.org/v2/"
headers = {'content-type': 'application/json'}
#NCBI API
ncbi_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#----------------------------------------------
def match_taxon(taxonName):
    resource_url = api_url + "tnrs/match_names"    
    payload = {
        'names': [taxonName], 
        'do_approximate_matching': 'false'
    }
    response = requests.post(resource_url, data=json.dumps(payload), headers=headers)
     
    data_json = json.loads(response.text)
    length = len(data_json['results']) 
    
    if length == 0:
        return -1 
    else: 
        return data_json['results'][0]['matches'][0]['ot:ottId']

#-------------------------------------------
def get_children(ottId):
    resource_url = api_url + "taxonomy/taxon"    
    payload = {
        'ott_id': ottId,
        'include_children': 'true'    
    }
    response = requests.post(resource_url, data=json.dumps(payload), headers=headers)
      
    return json.loads(response.text)

#----------------------------------------    
def get_species_from_highrank(highrankChildren):
    species_list = [] 
    #get all children of each higherankedChildren    
    for child in highrankChildren: 
 		species_lst = []  #temp species list
 		res_json = get_children(child['ot:ottId'])
 		children_lst = res_json['children']
 		if child['rank'] == 'genus':
 		 	#get all species from genus
 			if len(children_lst) == 0:
 				continue
 			species_lst = get_species_from_genus(children_lst)
 			#extend the species list with the species of this genus
 			species_list.extend(species_lst)
 		else:
 			highrankChildren.extend(children_lst) 
                                   
    return species_list

#-------------------------------------------
def get_species_from_genus(genusChildren):
    species_list = []
    #get all species of a genus 
    for child in genusChildren:
 		if child['rank'] == 'species':
 			species_list.append(child['ot:ottTaxonName'])            
        
    return species_list

#-------------------------------------------------    
def check_species_by_country(species, country):
    INaturalistApi_url = 'https://www.inaturalist.org/places.json'

    payload = {
        'taxon': species,
        'place_type': 'Country',
    }    
    
    matched_result = requests.get(INaturalistApi_url, params=payload)
    res_json = json.loads(matched_result.text) 
    
    countryList = []
    for place in res_json:
        countryList.append(place['name'].lower())
    country = country.lower()
    #commonList = list(set(countries).intersection(set(countryList)))
    
    if (country in countryList):
        return True
    else:
        return False

#---------------------------------------------------
def get_all_species(inputTaxon):
 	"""Gets all species that belong to a particular taxon
    
    **Note**> Maximum taxonomic rank allowed: ``family``. It may take longer time (more than 60s) to return output for input taxons higher than ``genus`` rank. 

	Example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.get_all_species("Vulpes")
	>>> print result
	{"execution_time": "11.33", "status_code": 200, "creation_time": "2017-07-02T18:09:04.415738", "taxon": "Vulpes", "total_names": 19, "service_url": "http://phylo.cs.nmsu.edu:5004/phylotastic_ws/ts/all_species?taxon=Vulpes", "message": "Success", "species": ["Vulpes mathisoni", "Vulpes minimus", "Vulpes cascadensis", "Vulpes kernensis", "Vulpes environmental sample", "Vulpes stenognathus", "Vulpes bengalensis", "Vulpes pallida", "Vulpes cana", "Vulpes chama", "Vulpes vulpes", "Vulpes lagopus", "Vulpes corsac", "Vulpes rueppellii", "Vulpes zerda", "Vulpes velox", "Vulpes macrotis", "Vulpes sp.", "Vulpes ferrilata"], "service_documentation": "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-6"}

    :param inputTaxon: Name of a taxon for which species needs to be found. 
    :type inputTaxon: string.  
    :returns: A json formatted string -- with a list of species names as the value of the ``species`` property. 

    """
 	start_time = time.time()

 	service_url = base_url + "all_species?taxon=" + inputTaxon
 	service_documentation = "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-6"

 	ott_id = match_taxon(inputTaxon)
 	if ott_id == -1:
 		final_result = {'taxon': inputTaxon,'species': [], 'message': 'No Taxon matched with %s' %(inputTaxon), 'status_code': 204}
 		len_splist = 0	
 	else: #taxon name matched	
 		species_list = []
 		
 		data_json = get_children(ott_id)
 		if data_json['rank'] == 'species' or data_json['rank'] == 'subspecies':
 			species_list.append(data_json['ot:ottTaxonName'])		
 		elif data_json['rank'] == 'genus':
 			species_list = get_species_from_genus(data_json['children'])
 		else:
 			species_list = get_species_from_highrank(data_json['children'])
 		len_splist = len(species_list)
	
 		#print species_list
 		#species_list.sort()
 	 	
 	end_time = time.time()
 	execution_time = end_time-start_time    
    #service result creation time
 	creation_time = datetime.datetime.now().isoformat()

 	if len_splist > 0:
 	 	final_result = {'taxon': inputTaxon,'species': species_list, 'message': 'Success', 'status_code': 200}
 	elif len_splist == 0 and ott_id != -1:	
 	 	final_result = {'taxon': inputTaxon,'species': species_list, 'message': 'No species found', 'status_code': 204}

 	final_result['creation_time'] = creation_time
 	final_result['execution_time'] = "{:4.2f}".format(execution_time)
 	final_result['total_names'] = len_splist
 	#final_result['source_urls'] = ["https://github.com/OpenTreeOfLife/opentree/wiki/Open-Tree-Taxonomy"]
 	#final_result['source_version'] = "ott2.9draft12"
 	final_result['service_url'] = service_url
 	final_result['service_documentation'] = service_documentation

 	return json.dumps(final_result)

#--------------------------------------------------
def get_country_species(inputTaxon, inputCountry):
 	"""Gets all species that belong to a particular taxon and established in a particular country.
    
    **Note**> Maximum taxonomic rank allowed: ``family``. It may take longer time (more than 60s) to return output for input taxons higher than ``genus`` rank. 

	Example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.get_country_species("Vulpes", "Nepal")
	>>> print result
	{"execution_time": "16.23", "status_code": 200, "creation_time": "2017-07-02T18:20:12.978379", "taxon": "Vulpes", "total_names": 2, "country": "Nepal", "service_url": "http://phylo.cs.nmsu.edu:5004/phylotastic_ws/ts/country_species?taxon=Vulpes&country=Nepal", "message": "Success", "species": ["Vulpes bengalensis", "Vulpes ferrilata"], "service_documentation": "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-7"}

    :param inputTaxon: Name of a taxon for which species needs to be found. 
    :type inputTaxon: string. 
	:param inputCountry: Name of a country in which species are established. 
    :type inputTaxon: string. 
 
    :returns: A json formatted string -- with a list of species names as the value of the ``species`` property. 

    """
 	start_time = time.time()

 	service_url = base_url + "country_species?taxon=" + inputTaxon + "&country=" + inputCountry 
 	service_documentation = "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-7"

 	ott_id = match_taxon(inputTaxon)
 	if ott_id == -1:
 		final_result = {'taxon': inputTaxon,'species': [], 'message': 'No Taxon matched with %s' %(inputTaxon), 'status_code': 204}
 		len_splist = 0
 	else: #taxon name matched and ott_id found
 		all_species_result = get_all_species(inputTaxon)  
  		all_species_json = json.loads(all_species_result)
 		status_code = all_species_json['status_code']
  		species_list = all_species_json['species']
 		message = all_species_json['message']	
 		#print all_species_result
 		
 		if status_code == 204:  #no taxon found or no species found
  			return all_species_json
 		elif status_code == 200:
 		 	species_lst = []
 		 	for species in species_list:
 				if check_species_by_country(species, inputCountry):
 					species_lst.append(species)
 			len_splist = len(species_lst)
  	
 	end_time = time.time()
 	execution_time = end_time-start_time    
    #service result creation time
 	creation_time = datetime.datetime.now().isoformat()

 	if  len_splist != 0:
 	 	final_result = {'taxon': inputTaxon,'species': species_lst, 'message': 'Success', 'status_code': 200}
   	elif len_splist == 0 and ott_id != -1:
 		final_result = {'taxon': inputTaxon,'species': species_lst, 'message': 'No species found on this country', 'status_code': 204}

 
 	final_result['creation_time'] = creation_time
 	final_result['execution_time'] = "{:4.2f}".format(execution_time)
 	final_result['total_names'] = len_splist
 	#final_result['source_urls'] = ["https://github.com/OpenTreeOfLife/opentree/wiki/Open-Tree-Taxonomy", "https://www.inaturalist.org"]
 	#final_result['source_version'] = "ott2.9draft12"
 	final_result['service_url'] = service_url
 	final_result['service_documentation'] = service_documentation	
 	final_result['country'] = inputCountry

 	return json.dumps(final_result)
 	
#=====================================================
#get genome ids available for a named taxonomic group
def find_genome_ids(taxonName):
 	api_func = "esearch.fcgi"	
 	api_url = ncbi_url + api_func    
 	payload = {
 		'retmax': 5000,
 		'retmode': 'json',
 		'db': 'genome',
 		'term': taxonName,
 		'tool': "phylotastic-services",
 		'email': "tayeen@nmsu.edu"      
    }
 	encoded_payload = urllib.urlencode(payload)
 	response = requests.get(api_url, params=encoded_payload, headers=headers) 
 	
 	gid_list = []
 	genome_response = {}    
 	genome_response['status_code'] = 200
 	genome_response['message'] = "Success"
 	
 	if response.status_code == requests.codes.ok:    
 		data_json = json.loads(response.text)
 		numResults = int(data_json['esearchresult']['count']) 
 		gid_list = data_json['esearchresult']['idlist']  
 	else: 
 		genome_response['status_code'] = 500
 		genome_response['message'] = "Error: Response error from NCBI esearch.fcgi API"

	genome_response['genome_ids'] = gid_list
 	
 	if numResults == 0:
  	 	genome_response['message'] = "No match found for term %s" %(taxonName)
 		genome_response['status_code'] = 204
 	
 	return genome_response 	

#--------------------------------------------   
#get the species ids associated with genome ids
def find_species_ids(genomeIds):
 	api_func = "elink.fcgi"	
 	api_url = ncbi_url + api_func    
 	payload = {
 		'retmax': 5000,
 		'retmode': 'json',
 		'dbfrom' : 'genome',
 		'db': 'taxonomy',
 		'id': genomeIds,
 		'tool': "phylotastic-services",
 		'email': "tayeen@nmsu.edu"
    }
 	encoded_payload = urllib.urlencode(payload)
 	response = requests.get(api_url, params=encoded_payload, headers=headers) 
 	#response = requests.post(api_url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})

 	sid_list = []
 	taxonomy_response = {}    
 	taxonomy_response['status_code'] = 200
 	taxonomy_response['message'] = "Success"

 	if response.status_code == requests.codes.ok:    
 		data_json = json.loads(response.text)
 		sid_list = data_json['linksets'][0]['linksetdbs'][0]['links'] 
 	else:
 		taxonomy_response['status_code'] = 500
 		taxonomy_response['message'] = "Error: Response error from NCBI elink.fcgi API"
 	
 	taxonomy_response['species_ids'] = sid_list

 	return taxonomy_response

#--------------------------------------------   
#get the species names associated with species ids
def get_species_names(speciesIds):
 	api_func = "esummary.fcgi"	
 	api_url = ncbi_url + api_func    
 	payload = {
 		'retmax': 5000,
 		'retmode': 'json',
 		'db': 'taxonomy',
 		'id': speciesIds,
 		'tool': "phylotastic-services",
 		'email': "tayeen@nmsu.edu"
    }
 	encoded_payload = urllib.urlencode(payload)
 	response = requests.get(api_url, params=encoded_payload, headers=headers) 
 	#response = requests.post(api_url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})

 	sname_list = []
 	taxonomy_response = {}    
 	taxonomy_response['status_code'] = 200
 	taxonomy_response['message'] = "Success"

 	if response.status_code == requests.codes.ok:    
 		data_json = json.loads(response.text)
 		uid_list = data_json['result']['uids']
 		for uid in uid_list:
 			sname_list.append(data_json['result'][str(uid)]['scientificname']) 
 	else:
 		taxonomy_response['status_code'] = 500
 		taxonomy_response['message'] = "Error: Response error from NCBI elink.fcgi API"
 	
 	taxonomy_response['species'] = sname_list

 	return taxonomy_response
 	
#----------------------------------------------
#form comma separated ids for the APIs 
def form_cs_ids(id_list):
 	str_ids = ""
 	length = len(id_list)
 	count = 0
 	for Id in id_list:
 		count = count + 1
 		str_ids = str_ids + str(Id)
 		if count != length:
 			str_ids = str_ids + ","
 			
 	return str_ids
 	
#---------------------------------------------------
def get_genome_species(inputTaxon):
 	"""Gets all species that belong to a particular taxon and have genome sequence in NCBI.
    
	Example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.get_genome_species("Felidae")
	>>> print result
	{"execution_time": "10.43", "status_code": 200, "creation_time": "2017-07-02T21:12:17.248633", "taxon": "Felidae", "total_names": 6, "source_urls": ["https://www.ncbi.nlm.nih.gov/taxonomy", "https://www.ncbi.nlm.nih.gov/genome"], "service_url": "http://phylo.cs.nmsu.edu:5004/phylotastic_ws/ts/ncbi/genome_species?taxon=Felidae", "message": "Success", "species": ["Panthera tigris amoyensis", "Panthera tigris altaica", "Acinonyx jubatus", "Panthera tigris", "Panthera pardus", "Felis catus"], "service_documentation": "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-9"}

    :param inputTaxon: Name of a taxon for which species needs to be found. 
    :type inputTaxon: string. 
	
    :returns: A json formatted string -- with a list of species names as the value of the ``species`` property. 

    """	
 	start_time = time.time()
 	service_url = "http://phylo.cs.nmsu.edu:5004/phylotastic_ws/ts/ncbi/genome_species?taxon=" + inputTaxon
 	service_documentation = "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-9"

 	final_result = {}	
 	g_response = find_genome_ids(inputTaxon)
 	
 	if g_response['status_code'] != 200:	 	
 		final_result = g_response
 	else:
 		str_gids = form_cs_ids(g_response['genome_ids'])
 		s_response = find_species_ids(str_gids)
 		if s_response['status_code'] != 200:
 			final_result = s_response
 		else:
 			str_sids = form_cs_ids(s_response['species_ids'])
 			final_result = get_species_names(str_sids)
	
 	end_time = time.time()
 	execution_time = end_time-start_time    
    #service result creation time
 	creation_time = datetime.datetime.now().isoformat()
 	
 	final_result['creation_time'] = creation_time
 	final_result['execution_time'] = "{:4.2f}".format(execution_time)
 	if final_result['status_code'] == 200: 
 		final_result['total_names'] = len(final_result['species'])
 	else:
 		final_result['total_names'] = 0 
 	final_result['source_urls'] = ["https://www.ncbi.nlm.nih.gov/taxonomy", "https://www.ncbi.nlm.nih.gov/genome"]
 	#final_result['source_version'] = "ott2.9draft12"
 	final_result['service_url'] = service_url
 	final_result['service_documentation'] = service_documentation	
 	final_result['taxon'] = inputTaxon

 	return json.dumps(final_result)
#--------------------------------------------------

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#if __name__ == '__main__':

	#inputTaxon = 'Vulpes' #genus
 	#inputTaxon = 'Felidae' #family
	#country = 'Nepal'
	#print get_all_species(inputTaxon)
	#print get_country_species(inputTaxon, country)
 	#print get_genome_species(inputTaxon)
