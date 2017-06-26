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
def get_sn_url(inputURL, sEngine):
    
    payload = {
        'url': inputURL,
        'engine': sEngine	
    }
    
    encoded_payload = urllib.urlencode(payload)
    response = requests.get(api_url, params=encoded_payload, headers=headers) 
    
    scientificNamesList = []

    if sEngine == 0:
       service_url = base_url + "names_url?url=" + inputURL
    else:
       service_url = base_url + "names_url?url=" + inputURL + "&engine=" + sEngine
     
    service_documentation = "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-1"

    if response.status_code == requests.codes.ok:    
        data_json = json.loads(response.text)
    else:
        return {'input_url': inputURL, 'scientificNames': scientificNamesList,'status_code': 500,
                'service_url': service_url, "service_url_doc": service_documentation, 'message': "Error extracting names using GNRD"} 
    
    token_result = get_token_result(data_json)
    
    if token_result['total'] == 0:
         return {'input_url': inputURL, 'scientificNames': scientificNamesList, 'status_code': 204, 
                 'service_url': service_url, "service_url_doc": service_documentation, 'message': "No scientific names found"} 
    else:
         scientificNamesList = get_sn(token_result['names'])
         parametersList = token_result['parameters']        
         
         return {'input_url': inputURL, 'parameters': parametersList, 'scientificNames': scientificNamesList, 'status_code': 200, 
                 'service_url': service_url, "service_url_doc": service_documentation, 'message': "Success"} 
     
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
def get_sn_text(inputTEXT, sEngine):
    payload = {
        'text': inputTEXT,
        'engine': sEngine
    }
    
    encoded_payload = urllib.urlencode(payload)
    response = requests.get(api_url, params=encoded_payload, headers=headers) 
 
    scientificNamesList = []
    
    if sEngine == 0:
       service_url = base_url + "names_text?text=" + inputTEXT
    else:
       service_url = base_url + "names_text?text=" + inputTEXT + "&engine=" + sEngine
     
    service_documentation = "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-2"    

    if response.status_code == requests.codes.ok:    
        data_json = json.loads(response.text)
    else:
        return {'input_text': inputTEXT, 'scientificNames': scientificNamesList, 'status_code': 500, 
                'service_url': service_url, "service_url_doc": service_documentation, 'message': "Error extracting names using GNRD"} 
    
    token_result = get_token_result(data_json)
    
    if token_result['total'] == 0:
         return {'input_text': inputTEXT, 'scientificNames': scientificNamesList, 'status_code': 204, 
                 'service_url': service_url, "service_url_doc": service_documentation, 'message': "No scientific names found"} 
    else:
         scientificNamesList = get_sn(token_result['names'])
         parametersList = token_result['parameters']
          
         return {'input_text': inputTEXT, 'parameters': parametersList, 'scientificNames': scientificNamesList, 'status_code': 200, 
                 'service_url': service_url, "service_url_doc": service_documentation, 'message': "Success"} 

#--------------------------------------
def extract_names_URL(inputURL, sEngine=0):
    """Extracts scientific names from a web URL
    
	For example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.extract_names_URL("https://en.wikipedia.org/wiki/Plain_pigeon")
	>>> print result
	{"parameters": {"engine": 0, "best_match_only": false, "data_source_ids": [], "detect_language": true, "preferred_data_sources": [], "all_data_sources": false, "return_content": false}, "execution_time": "1.44", "status_code": 200, "creation_time": "2017-06-26T12:29:22.770155", "input_url": "https://en.wikipedia.org/wiki/Plain_pigeon", "scientificNames": ["Patagioenas inornata wetmorei", "Animalia", "Chordata", "Aves", "Columbiformes", "Columbidae", "Patagioenas", "Patagioenas inornata", "Columba inornata", "P. flavirostria", "P. oenops", "Hispaniola"], "service_url": "http://phylo.cs.nmsu.edu:5004/phylotastic_ws/fn/names_url?url=https://en.wikipedia.org/wiki/Plain_pigeon", "service_url_doc": "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-1", "total_names": 12, "message": "Success"}

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

    final_result['creation_time'] = creation_time
    final_result['execution_time'] = "{:4.2f}".format(execution_time) 
    final_result['total_names'] = len(final_result['scientificNames'])

    return json.dumps(final_result)

#----------------------------------------------------
def extract_names_TEXT(inputTEXT, sEngine=0):
    """Extracts scientific names from free-form text
    
	For example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.extract_names_TEXT("Formica polyctena is a species of European red wood ant in the genus Formica.")
	>>> print result
	{"parameters": {"engine": 0, "best_match_only": false, "data_source_ids": [], "detect_language": true, "preferred_data_sources": [], "all_data_sources": false, "return_content": false}, "execution_time": "0.48", "status_code": 200, "creation_time": "2017-06-26T13:14:39.213865", "scientificNames": ["Formica polyctena"], "service_url": "http://phylo.cs.nmsu.edu:5004/phylotastic_ws/fn/names_text?text=Formica polyctena is a species of European red wood ant in the genus Formica.", "service_url_doc": "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-2", "total_names": 1, "message": "Success", "input_text": "Formica polyctena is a species of European red wood ant in the genus Formica."}

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
    final_result['creation_time'] = creation_time
    final_result['execution_time'] = "{:4.2f}".format(execution_time)
    final_result['total_names'] = len(final_result['scientificNames'])
    
    return json.dumps(final_result)	    
   
#--------------------------------------------
