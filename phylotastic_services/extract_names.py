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
    try: 
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
    
    except ValueError:
          return {'input_url': inputURL, 'scientificNames': [], 'status_code': 500, 'message': "No JSON object could be decoded from GNRD response"}      

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
        
    #print "Waiting for the token to be activated"    
    #time.sleep(20)
    
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

        #return {'input_text': inputTEXT, 'scientificNames': scientificNamesList, 'status_code': statuscode, 'message': msg} 
        return {'scientificNames': scientificNamesList, 'status_code': statuscode, 'message': msg} 
    
    token_result = get_token_result(data_json)
    
    if token_result['total'] == 0:
         return {'scientificNames': scientificNamesList, 'status_code': 200, 'message': "No scientific names found"} 
    else:
         scientificNamesList = get_sn(token_result['names'])
         parametersList = token_result['parameters']
         #scientificNamesList = uniquify(all_scientificNamesList) 
         return {'gnrd_parameters': parametersList, 'scientificNames': scientificNamesList, 'status_code': 200,'message': "Success"} 

#-----------------------------------------------------------
#----------------------TaxonFinder(http://taxonfinder.org/api)------------------------------------
#get scientific names from URL using TaxonFinder 
def get_tf_sn_url(inputURL):
    payload = {
        'url': inputURL	
    }
    
    taxon_finder_api = "http://taxonfinder.org/api/find?"
    #encoded_payload = urllib.urlencode(payload)
    response = requests.get(taxon_finder_api, params=payload) 
    #print response.text
     
    if response.status_code == requests.codes.ok:    
        data_json = json.loads(response.text)
    else:
        data_json = json.loads(response.text)
        if 'message' in data_json:
           msg = "TaxonFinder Error: "+data_json['message']
        else:
           msg = "Error: Response error while extracting names using TaxonFinder"
        if 'status' in data_json:
           statuscode = data_json['status']
        else:
           statuscode = 500

        return {'input_url': inputURL, 'scientificNames': scientificNamesList, 'status_code': statuscode, 'message': msg} 
    
    scientificNamesList = get_tf_names(data_json)
    
    if len(scientificNamesList) == 0:
         return {'input_url': inputURL, 'scientificNames': scientificNamesList, 'status_code': 200, 'message': "No scientific names found"} 
    else:
         return {'input_url': inputURL, 'scientificNames': scientificNamesList, 'status_code': 200, 'message': "Success"} 

#-------------------------------------------
#get scientific names from TEXT using TaxonFinder
def get_tf_sn_text(inputTEXT):
    payload = {
        'text': inputTEXT	
    }
    
    taxon_finder_api = "http://taxonfinder.org/api/find?"
    #encoded_payload = urllib.urlencode(payload)
    response = requests.post(taxon_finder_api, data=payload) 
         
    if response.status_code == requests.codes.ok:    
        data_json = json.loads(response.text)
    else:
        data_json = json.loads(response.text)
        if 'message' in data_json:
           msg = "TaxonFinder Error: "+data_json['message']
        else:
           msg = "Error: Response error while extracting names using TaxonFinder"
        if 'status' in data_json:
           statuscode = data_json['status']
        else:
           statuscode = 500

        return {'scientificNames': scientificNamesList, 'status_code': statuscode, 'message': msg} 
    
    scientificNamesList = get_tf_names(data_json)
    
    if len(scientificNamesList) == 0:
         return {'scientificNames': scientificNamesList, 'status_code': 200, 'message': "No scientific names found"} 
    else:
         return {'scientificNames': scientificNamesList, 'status_code': 200, 'message': "Success"} 
     
#--------------------------------------------
def get_tf_names(data_json):
    snlist = []
    for element in data_json:
        scName = element['name']
        #print scName
        # Remove any parenthesis
        scName = re.sub(r'[()]', "", scName)
        if scName not in snlist: # Check for duplicate
           snlist.append(str(scName))   
    
    return snlist

#--------------------------------------
def extract_names_URL(inputURL, source="gnrd", sEngine=0):
    """Extracts scientific names from a web URL
    
	For example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.extract_names_URL("https://en.wikipedia.org/wiki/Plain_pigeon", "gnrd")
	>>> print result
	{"status_code": 200, "input_url": "https://en.wikipedia.org/wiki/Plain_pigeon", "scientificNames": ["Patagioenas inornata wetmorei", "Animalia", "Chordata", "Aves", "Columbiformes", "Columbidae", "Patagioenas", "Patagioenas inornata", "Columba inornata", "P. flavirostria", "P. oenops", "Hispaniola"], "meta_data": {"execution_time": 1.16, "creation_time": "2018-01-15T22:10:17.313609", "source_urls": ["http://gnrd.globalnames.org/"]}, "total_names": 12, "message": "Success", "gnrd_parameters": {"engine": 0, "best_match_only": false, "data_source_ids": [], "detect_language": true, "preferred_data_sources": [], "all_data_sources": false, "return_content": false}}

    :param inputURL: A url of a web page from which scientific names need to be extracted. 
    :type inputURL: str.
    :param source: The source tool to use for extracting names. "gnrd" (default) for using Global Names recognition and discovery, "taxonfinder" for using taxonfinder.org  
    :type source: str.      
    :param sEngine: Name discovery engine to be used for extracting names. 1 for TaxonFinder, 2 for NetiNeti, or 0 (default) for both 
    :type sEngine: int. 
    :returns: A json formatted string -- with a list of names as the value of the ``scientificNames`` property. 

    """
    #service execution time
    start_time = time.time()
    if source == "gnrd":
       final_result = get_sn_url(inputURL, sEngine)
    elif source == "taxonfinder":
       final_result = get_tf_sn_url(inputURL)
    else:
       return {'status_code': 400, 'message': "Error: Invalid source name"} 

    end_time = time.time()
    execution_time = end_time-start_time

    #service result creation time
    creation_time = datetime.datetime.now().isoformat()

    meta_data = {'creation_time': creation_time, 'execution_time': float("{:4.2f}".format(execution_time)), 'source_urls': ["http://gnrd.globalnames.org/"] }

    final_result['meta_data'] = meta_data
    final_result['total_names'] = len(final_result['scientificNames'])

    return json.dumps(final_result)

#----------------------------------------------------
def extract_names_TEXT(inputTEXT, source="gnrd", sEngine=0):
    """Extracts scientific names from free-form text
    
	For example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.extract_names_TEXT("Formica polyctena is a species of European red wood ant in the genus Formica." "taxonfinder")
	>>> print result
	{"status_code": 200, "scientificNames": ["Formica polyctena"], "meta_data": {"execution_time": 0.29, "creation_time": "2018-05-20T18:59:10.951318", "source_urls": ["http://taxonfinder.org/"]}, "total_names": 1, "message": "Success"}

    :param inputTEXT: Text content to extract scientific names from. 
    :type inputTEXT: str.
    :param source: The source tool to use for extracting names. "gnrd" (default) for using Global Names recognition and discovery, "taxonfinder" for using taxonfinder.org  
    :type source: str.     
    :param sEngine: Name discovery engine to be used for extracting names. 1 for TaxonFinder, 2 for NetiNeti, or 0 (default) for both 
    :type sEngine: int. 
    :returns: A json formatted string -- with a list of names as the value of the ``scientificNames`` property. 

    """
    start_time = time.time()
    if source == "gnrd":
       final_result = get_sn_text(inputTEXT, sEngine)
    elif source == "taxonfinder":
       final_result = get_tf_sn_text(inputTEXT)
    else:
       return {'status_code': 400, 'message': "Error: Invalid source name"} 
        
    end_time = time.time()
    execution_time = end_time-start_time
    
    #service result creation time
    creation_time = datetime.datetime.now().isoformat()
    meta_data = {'creation_time': creation_time, 'execution_time': float("{:4.2f}".format(execution_time)), 'source_urls': ["http://gnrd.globalnames.org/"] }

    final_result['meta_data'] = meta_data

    final_result['total_names'] = len(final_result['scientificNames'])
    
    return json.dumps(final_result)	    
   
#--------------------------------------------
