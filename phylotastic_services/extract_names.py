#find scientific names service: version 0.1
import json
import time
import requests
import re
import ast
import urllib
import datetime

api_url = "http://gnrd.globalnames.org/name_finder.json?"
headers = {'content-type': 'application/json'}
base_url = "http://phylo.cs.nmsu.edu:5004/phylotastic_ws/fn/"

#-----------------------------------------
#get scientific names from URL
def get_sn_url(inputURL, sEngine=0):
    payload = {
        'url': inputURL,
        'engine': sEngine	
    }
    
    encoded_payload = urllib.urlencode(payload)
    response = requests.get(api_url, params=encoded_payload, headers=headers) 
    
    scientificNamesList = []
     
    if response.status_code == requests.codes.ok:    
        data_json = json.loads(response.text)
    else:
        data_json = json.loads(response.text)
        if 'message' in data_json:
           msg = "GNRD Error: "+data_json['message']
        else:
           msg = "Error: Response error while extracting names using GNRD"
        if 'status' in data_json:
           statuscode = data_json['status']
        else:
           statuscode = 500

        return {'input_url': inputURL, 'scientificNames': scientificNamesList, 'status_code': statuscode, 'message': msg} 
    
    token_result = get_token_result(data_json)
    
    if token_result['total'] == 0:
         return {'input_url': inputURL, 'scientificNames': scientificNamesList, 'status_code': 200, 'message': "No scientific names found"} 
    else:
         scientificNamesList = get_sn(token_result['names'])
         parametersList = token_result['parameters']        
         #scientificNamesList = uniquify(all_scientificNamesList) 
         return {'input_url': inputURL, 'gnrd_parameters': parametersList, 'scientificNames': scientificNamesList, 'status_code': 200, 'message': "Success"}
     
#----------------------------------------------    
#get scientific names from final api-result
def get_sn(namesList):
    snlist = []
    uclist = []    
    for sn in namesList:
        #scName = element['scientificName'].replace(' ', '+')
        scName = sn['scientificName']       
        if is_ascii(scName): #check if there is any string with unicode character
            # Remove any parenthesis
            scName = re.sub(r'[()]', "", scName)
            if scName not in snlist: # Check for duplicate
               snlist.append(str(scName))    
        #else:         
        #    uclist.append(scName)
    
    return snlist; 

#------------------------------------------------
def is_ascii(str_val):
    return bool(re.match(r'[\x00-\x7F]+$', str_val))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#get the final-api result using the token
def get_token_result(response_json):
        
    #get the token value from token url
    token_url = response_json['token_url']
    tokenURL, token = token_url.split('=', 1)
    str_token = str(token);
        
    payload = {
        'token': str_token,
    }
    
    encoded_payload = urllib.urlencode(payload)
    
    while True:
        token_result = requests.get(api_url, params=encoded_payload, headers=headers)
        result_json = json.loads(token_result.text)
        if token_result.status_code == result_json['status']:
           return result_json 

#---------------------------------------------------
#get scientific names from Text
def get_sn_text(inputTEXT, sEngine=0):
    payload = {
        'text': inputTEXT,
        'engine': sEngine
    }
    
    #encoded_payload = urllib.urlencode(payload)
    #response = requests.get(api_url, params=encoded_payload, headers=headers) 
    response = requests.post(api_url, data=payload) 

    scientificNamesList = []
    
    if response.status_code == requests.codes.ok:    
        data_json = json.loads(response.text)
    else:
        data_json = json.loads(response.text) 
        if 'message' in data_json:
           msg = "GNRD Error: "+data_json['message']
        else:
           msg = "Error: Response error while extracting names using GNRD"
        if 'status' in data_json:
           statuscode = data_json['status']
        else:
           statuscode = 500

        return {'input_text': inputTEXT, 'scientificNames': scientificNamesList, 'status_code': statuscode, 'message': msg} 
    
    token_result = get_token_result(data_json)
    
    if token_result['total'] == 0:
         return {'input_text': inputTEXT, 'scientificNames': scientificNamesList, 'status_code': 200, 'message': "No scientific names found"} 
    else:
         scientificNamesList = get_sn(token_result['names'])
         parametersList = token_result['parameters']
         #scientificNamesList = uniquify(all_scientificNamesList) 
         return {'input_text': inputTEXT, 'gnrd_parameters': parametersList, 'scientificNames': scientificNamesList, 'status_code': 200,'message': "Success"}  

#--------------------------------------
def extract_names_URL(inputURL, sEngine=0):
    """Extracts scientific names from a web URL
    
	For example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.extract_names_URL("https://en.wikipedia.org/wiki/Plain_pigeon")
	>>> print result
	{"status_code": 200, "input_url": "https://en.wikipedia.org/wiki/Plain_pigeon", "scientificNames": ["Patagioenas inornata wetmorei", "Animalia", "Chordata", "Aves", "Columbiformes", "Columbidae", "Patagioenas", "Patagioenas inornata", "Columba inornata", "P. flavirostria", "P. oenops", "Hispaniola"], "meta_data": {"execution_time": 1.16, "creation_time": "2018-01-15T22:10:17.313609", "source_urls": ["http://gnrd.globalnames.org/"]}, "total_names": 12, "message": "Success", "gnrd_parameters": {"engine": 0, "best_match_only": false, "data_source_ids": [], "detect_language": true, "preferred_data_sources": [], "all_data_sources": false, "return_content": false}}

    :param inputURL: A url of a web page from which scientific names need to be extracted. 
    :type inputURL: str. 
    :param sEngine: Name discovery engine to be used for extracting names. 1 for TaxonFinder, 2 for NetiNeti, or 0 (default) for both 
    :type sEngine: int. 
    :returns: A json formatted string -- with a list of names as the value of the ``scientificNames`` property. 

    """
    #service execution time
    start_time = time.time()
    final_result = get_sn_url(inputURL, sEngine)    
    end_time = time.time()
    execution_time = end_time-start_time

    #service result creation time
    creation_time = datetime.datetime.now().isoformat()

    meta_data = {'creation_time': creation_time, 'execution_time': float("{:4.2f}".format(execution_time)), 'source_urls': ["http://gnrd.globalnames.org/"] }

    final_result['meta_data'] = meta_data
    final_result['total_names'] = len(final_result['scientificNames'])

    return json.dumps(final_result)

#----------------------------------------------------
def extract_names_TEXT(inputTEXT, sEngine=0):
    """Extracts scientific names from free-form text
    
	For example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.extract_names_TEXT("Formica polyctena is a species of European red wood ant in the genus Formica.")
	>>> print result
	{"status_code": 200, "scientificNames": ["Formica polyctena"], "meta_data": {"execution_time": 0.29, "creation_time": "2018-01-15T22:11:16.099248", "source_urls": ["http://gnrd.globalnames.org/"]}, "total_names": 1, "message": "Success", "gnrd_parameters": {"engine": 0, "best_match_only": false, "data_source_ids": [], "detect_language": true, "preferred_data_sources": [], "all_data_sources": false, "return_content": false}, "input_text": "Formica polyctena is a species of European red wood ant in the genus Formica."}

    :param inputTEXT: Text content to extract scientific names from. 
    :type inputTEXT: str. 
    :param sEngine: Name discovery engine to be used for extracting names. 1 for TaxonFinder, 2 for NetiNeti, or 0 (default) for both 
    :type sEngine: int. 
    :returns: A json formatted string -- with a list of names as the value of the ``scientificNames`` property. 

    """
    start_time = time.time()
    final_result = get_sn_text(inputTEXT, sEngine)    
    end_time = time.time()
    execution_time = end_time-start_time
    
    #service result creation time
    creation_time = datetime.datetime.now().isoformat()
    meta_data = {'creation_time': creation_time, 'execution_time': float("{:4.2f}".format(execution_time)), 'source_urls': ["http://gnrd.globalnames.org/"] }

    final_result['meta_data'] = meta_data

    final_result['total_names'] = len(final_result['scientificNames'])
    
    return json.dumps(final_result)	    
   
#--------------------------------------------
