"""
**common_names** Module is for getting scientific names of species from their corresponding common names 
"""

import re
import json
import requests
import time
import datetime 
import urllib
import ConfigParser
from bs4 import BeautifulSoup
from os.path import dirname, abspath


#----------------------------------------------
NCBI_base_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
TROPICOS_base_url = "http://services.tropicos.org/Name/"
ITIS_base_url = "https://www.itis.gov/ITISWebService/jsonservice/ITISService/"
ITIS_source_info_base = "https://www.itis.gov/ITISWebService/jsonservice/ITISService/getFullRecordFromTSN?tsn="
#-----------------------------------------------------
#====================================================
def search_name_NCBI(commonName, best_match):
	api_url = "https://www.ncbi.nlm.nih.gov/taxonomy/?"

	taxonomy_response = {}    
	taxonomy_response['status_code'] = 200
 	taxonomy_response['message'] = "Success"
	
	payload = {'term': commonName}
	encoded_payload = urllib.urlencode(payload)
	response_html = requests.get(api_url, params=encoded_payload) 
	
	match_name_info = {'searched_name': commonName}
	match_name_list = []

	if response_html.status_code == requests.codes.ok:
		#print response_html.text	 	
		soup = BeautifulSoup(response_html.text, "lxml")
		match_name_list = extract_sc_names_info(soup, not best_match) #best match true = don't want multiple results	
	else:
		taxonomy_response['status_code'] = 500
		taxonomy_response['message'] = "Error: Could not parse retrieve data"

	match_name_info['matched_names'] = match_name_list
	taxonomy_response['result'] = match_name_info 

	return taxonomy_response

#----------------------------------------------
#get multiple results
def extract_sc_names_info(SoupObj, multiple=False):
	divRprtTags = SoupObj.find_all("div", {"class": "rprt"})
	sc_names_list = []

	if len(divRprtTags) == 0:
		return sc_names_list	#no info found	
	else:
		for indx, divtag in enumerate(divRprtTags):
			sc_name_info = {}
			aTags = divtag.find_all("a")
			#extract scientific name
			sc_name = aTags[0].text
			sc_name_link = aTags[0].attrs['href']
			ncbi_id = sc_name_link[sc_name_link.rfind("=")+1:]		
			sc_info_link = "https://www.ncbi.nlm.nih.gov" + sc_name_link
			#print sc_info_link
		
			divSuppTag = divtag.find_all("div", {"class": "supp"})

			extra_info = extract_more_info(divSuppTag)
			sc_name_info['scientific_name'] = sc_name
			sc_name_info['rank'] = extra_info['rank']
			sc_name_info['common_name'] = extra_info['commonName']
			sc_name_info['identifier'] = ncbi_id 
			sc_name_info['source_info_url'] = sc_info_link
			sc_names_list.append(sc_name_info)
			if not multiple:
				break 
	
	return	sc_names_list

#----------------------------------------------
def extract_more_info(divSuppTag):
	#divSuppTag = SoupObj.find_all("div", {"class": "supp"})
	
	info = {}	
	if len(divSuppTag) == 0:
		info = None	#no info found	
	else:
		info_list = divSuppTag[0].text.split(",")
		#print info_list
		try:
			if len(info_list) >= 3:
				gen_comm_name_raw = info_list[0].strip()
				gen_comm_name =  gen_comm_name_raw[1:len(gen_comm_name_raw)-1] #Genbank common name
				rank = info_list[1].strip()
				#blast_name = info_list[2]
			elif len(info_list) >= 2:
				gen_comm_name = None
				rank = info_list[0].strip()

			info = {'commonName': gen_comm_name, 'rank': rank}
			#info = {'common_name': gen_comm_name, 'rank': rank, 'inherited_blast_name': blast_name}
		except IndexError:
			info = None
		except Exception as e:
			info = None
	
	return info 	

#===================================================
def search_name_ITIS(commonName, best_match):
	api_url = ITIS_base_url + "searchByCommonName?"

	itis_response = {}    
	itis_response['status_code'] = 200
 	itis_response['message'] = "Success"
	
	payload = {'srchKey': commonName}
	encoded_payload = urllib.urlencode(payload)
	response = requests.get(api_url, params=encoded_payload) 
	
	match_name_info = {'searched_name': commonName}
	match_name_list = []
	
	if response.status_code == requests.codes.ok:
		#print response.text
		cm_name_key_list = extract_name_info(response.text)
		#empty list means: No common name matched
		sc_name_info = {}
		if len(cm_name_key_list) != 0:
			if best_match:  #best match result
				best_matched_key, cm_name = find_best_match_key(commonName, cm_name_key_list)
				if best_matched_key is None:
					sc_name_info['scientific_name'] = search_key(cm_name_key_list[0][1])
					sc_name_info['common_name'] = cm_name_key_list[0][0]
					sc_name_info['identifier'] = cm_name_key_list[0][1]
					sc_name_info['source_info_url'] = ITIS_source_info_base + str(cm_name_key_list[0][1])
				else:
					sc_name_info['scientific_name'] = search_key(best_matched_key)
					sc_name_info['common_name'] = cm_name
					sc_name_info['identifier'] = best_matched_key
					sc_name_info['source_info_url'] = ITIS_source_info_base + str(best_matched_key)

				match_name_list.append(sc_name_info)
			else: #multiple results
				match_name_list = extract_sc_names(cm_name_key_list) 		
	else:
		itis_response['status_code'] = 500
		itis_response['message'] = "ITIS response Error: Could not retrieve data"

	match_name_info['matched_names'] = match_name_list
	itis_response['result'] = match_name_info 

	return itis_response

#---------------------------------------------------
def extract_sc_names(cm_name_list):
	matched_results = []
	
	for indx, (cm_name, cm_key) in enumerate(cm_name_list):
		sc_name_info = {}	
		sc_name_info['scientific_name'] = search_key(cm_key)
		sc_name_info['common_name'] = cm_name
		sc_name_info['identifier'] = cm_key
		sc_name_info['source_info_url'] = ITIS_source_info_base + str(cm_key)
		matched_results.append(sc_name_info)

	return matched_results

#----------------------------------------------------
def extract_name_info(ITIS_json_resp):
	found_common_names = []
	json_content = json.loads(ITIS_json_resp)
	
	if len(json_content['commonNames']) == 1 and json_content['commonNames'][0] is None:
		return found_common_names

	for cm_nm_obj in json_content['commonNames']:			
		cm_name = cm_nm_obj['commonName']
		cm_lang = cm_nm_obj['language'] 
		cm_tsn = cm_nm_obj['tsn']
		#print ("%s, %s")%(cm_name, cm_tsn)
		if cm_lang == "English": #get only english common names
			found_common_names.append( (cm_name, cm_tsn) )
	 
	return found_common_names

#-----------------------------------------------------
def find_best_match_key(input_name, cm_name_key_list):
	best_match_key = second_best_match_key = None
	best_match_cm_name = second_best_match_cm_name = None
	for indx, (cm_name, cm_tsn) in enumerate(cm_name_key_list):
		cleaned_input_name = re.sub(r"\s+"," ", input_name.strip())
		cm_name_lower = cm_name.lower()
		#print ("%s, %s, %s")%(input_name, cm_name_lower, cm_tsn)
		if best_match_key is None and cleaned_input_name.lower() == cm_name_lower:
			best_match_key = cm_tsn
			best_match_cm_name = cm_name
		elif second_best_match_key is None and cleaned_input_name.lower() in cm_name_lower:
			second_best_match_key = cm_tsn
			second_best_match_cm_name = cm_name	

	#print ("%s, %s, %s, %s")%(best_match_key, best_match_cm_name, second_best_match_key, second_best_match_cm_name)
	if best_match_key is not None:
		return best_match_key, best_match_cm_name 
	else:
		return second_best_match_key, second_best_match_cm_name

#--------------------------------------------------------
def search_key(key):
	api_url = ITIS_base_url+"searchForAnyMatch?"

	payload = {'srchKey': key}
	encoded_payload = urllib.urlencode(payload)
	response = requests.get(api_url, params=encoded_payload) 
	
	if response.status_code == requests.codes.ok:
		json_resp = json.loads(response.text)
		name_info = json_resp['anyMatchList'][0]['sciName']
	else:
		name_info = None

	return name_info

#==================================================
def get_api_key():
	config = ConfigParser.ConfigParser()
	current_dir = dirname(abspath(__file__))
	config.read(current_dir + "/"+ "service.cfg")
	
	tropicos_api_key = config.get('TROPICOS', 'api_key')

	return tropicos_api_key

#----------------------------------
def search_name_TROPICOS(commonName, best_match):
	api_url = TROPICOS_base_url + "Search?"
	Tropicos_API_Key = get_api_key()
	match_type = "exact" if best_match else "wildcard" 	

	response = {}    
	response['status_code'] = 200
 	response['message'] = "Success"
	
	payload = {
		'commonname': commonName,
		'type': match_type,
		'apikey': Tropicos_API_Key,
		'format': "json"	
	}

	api_response = requests.get(api_url, params=payload) 
	
	match_name_info = {'searched_name': commonName}
	match_name_list = []

	if api_response.status_code == requests.codes.ok:
		#print api_response.text	 	
		match_name_list = extract_sc_names_info_TRPC(api_response.text, not best_match) #best match true = don't want multiple results	
	else:
		response['status_code'] = 500
		response['message'] = "Error: Retrieving data from Tropicos API"

	match_name_info['matched_names'] = match_name_list
	response['result'] = match_name_info 

	return response

#----------------------------------------------
#get multiple results
def extract_sc_names_info_TRPC(respText, multiple=False):
	sc_names_list = []
	json_resp = json.loads(respText)
	
	if 'Error' in json_resp[0]: #[{u'Error': u'No names were found'}]
		return sc_names_list

	for match in json_resp:
		sc_name_info = search_name_key(match['NameId'])
		if sc_name_info is not None:
			sc_names_list.append(sc_name_info)			
		if not multiple:
			break 
			
	return sc_names_list

#-------------------------------------------
def search_name_key(key):
	api_url = TROPICOS_base_url+str(key)

	payload = {'apikey': get_api_key(), 'format': "json"}
	response = requests.get(api_url, params=payload) 
	
	name_info = {}
	if response.status_code == requests.codes.ok:
		json_resp = json.loads(response.text)
		name_info['scientific_name'] = json_resp['ScientificName']
		name_info['rank'] = json_resp['Rank']
		#name_info['common_name'] = extra_info['commonName']
		name_info['identifier'] = json_resp['NameId'] 
		name_info['source_info_url'] = json_resp['Source']
	else:
		name_info = None

	return name_info

#---------------------------------------------------
def get_scientific_names(inputNameList, source="NCBI", best_match=True):
 	"""Get scientific names of a list of species from their common names (vernacular names)
    
	For example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.get_scientific_names(["domestic cattle","blue whale"], "ITIS")
	>>> print result
	{"status_code": 200, "message": "Success", "result": [{"matched_names": [{"scientific_name": "Bos taurus", "common_name": "domestic cattle (feral)", "identifier": "183838", "source_info_url": "https://www.itis.gov/ITISWebService/jsonservice/ITISService/getFullRecordFromTSN?tsn=183838"}], "searched_name": "domestic cattle"}, {"matched_names": [{"scientific_name": "Balaenoptera musculus", "common_name": "Blue Whale", "identifier": "180528", "source_info_url": "https://www.itis.gov/ITISWebService/jsonservice/ITISService/getFullRecordFromTSN?tsn=180528"}], "searched_name": "blue whale"}], "metadata": {"execution_time": "3.99", "creation_time": "2018-06-09T17:44:38.256939", "source_urls": ["https://www.itis.gov/ws_description.html"]}}

    :param inputNameList: A list of common names for which to find scientific names. 
    :type inputNameList: list of str.
    :param source: The source tool to use for finding scientific names. Valid values include: ``NCBI`` (default), ``ITIS``, ``TROPICOS``.  
    :type source: str.     
    :param best_match: A boolean value to specify whether to return the best match result or multiple results. `True` (default), If `False` multiple matches (if available) for each common name in the input list will be returned. 
    :type best_match: boolean. 
    :returns: A json formatted string -- with a list of matched names. 

    """	
 	start_time = time.time()
 	
	final_result = {'status_code': 200, 'message': "Success" }
	if source not in ["NCBI", "ITIS", "TROPICOS"]:
		return {'status_code': 400, 'message': "Error: 'source' parameter must have a valid value"}

	results = []
	for inputName in inputNameList:
		if source == "NCBI":
			match_result = search_name_NCBI(inputName, best_match)
			source_urls = ["https://www.ncbi.nlm.nih.gov/taxonomy"]
		elif source == "ITIS":
			match_result = search_name_ITIS(inputName, best_match)
			source_urls = ["https://www.itis.gov/ws_description.html"]
		elif source == "TROPICOS":
			match_result = search_name_TROPICOS(inputName, best_match)
			source_urls = ["http://services.tropicos.org/"] 

		if match_result['status_code'] == 200:
			results.append(match_result['result'])

	final_result['result'] = results

	end_time = time.time()
 	execution_time = end_time-start_time    
    
	#service result creation time
 	creation_time = datetime.datetime.now().isoformat()

	final_result['metadata'] = {'creation_time': creation_time, 'execution_time': "{:4.2f}".format(execution_time), 'source_urls': source_urls}   	 
 	
 	return json.dumps(final_result)
#--------------------------------------------------
