#resolver service: version 0.1
import json
import time
import requests
import re
import ast
import urllib
import datetime


api_url = "http://resolver.globalnames.org/name_resolvers.json?"
headers = {'content-type': 'application/json'}
base_url = "http://phylo.cs.nmsu.edu:5004/phylotastic_ws/tnrs/"

#~~~~~~~~~~~~~~~~~~~~ (GlobalNamesResolver-TNRS)~~~~~~~~~~~~~~~~~~~~~~~~~~~
#resolve scientific names
def resolve_sn_gnr(scNames, post):
    payload = {
        'names': scNames,
        'best_match_only': 'true'
    }
    
    encoded_payload = urllib.urlencode(payload)
    response = requests.get(api_url, params=encoded_payload, headers=headers) 
    
    resolvedNamesList = [] 
    
    if response.status_code == requests.codes.ok:    
        data_json = json.loads(response.text)
        rsnames_list = data_json['data']
        parameters_list = data_json['parameters']   
        for element in rsnames_list:
            namesList = {}
            namesList['search_string'] = element['supplied_name_string']
            namesList['resolver_name'] = 'GNR'
            if 'results' in element:
            	rsname = element['results'][0]['canonical_form']       	
            	namesList['matched_name'] =  rsname
            	namesList['match_type'] = 'Exact' if element['results'][0]['match_type'] == 1 else 'Fuzzy'
            	namesList['synonyms'] = []
            	namesList['taxon_id'] = element['results'][0]['taxon_id']		
            else:
                namesList['matched_name'] = ""
            resolvedNamesList.append(namesList)

 	    status_code = 200
        message = "Success" 
    else:
        status_code = 500
        message = "Error resolving names with GNR"

    service_documentation = "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-4"

    return {'resolvedNames': resolvedNamesList, 'parameters': parameters_list, "service_url_doc": service_documentation, 'status_code': status_code, 'message': message}
        
#----------------------------------------------    

#~~~~~~~~~~~~~~~~~~~~ Process Scientific Names List ~~~~~~~~~~~~~~~~~~~~~~~~~~~
def make_api_friendly_list(scNamesList):
    #process list    
    ListSize = len(scNamesList)    
    
    count = 0;
    TobeResolvedNames = ''
    
    for str_element in scNamesList:
        count += 1
        if(count != ListSize):
            str_element += '||' 
        TobeResolvedNames += str_element
    
    #print "List size:"+ str(ListSize)    
    return TobeResolvedNames
                

#~~~~~~~~~~~~~~~~~~~~ (OpenTree-TNRS)~~~~~~~~~~~~~~~~~~~~~~~~~~~
def resolve_sn_ot(scNames, do_fuzzy_match, multi_match):
    opentree_api_url = 'https://api.opentreeoflife.org/v2/tnrs/match_names'
    
    payload = {
        'names': scNames,
 		'do_approximate_matching': do_fuzzy_match
    }
    jsonPayload = json.dumps(payload)
   
    response = requests.post(opentree_api_url, data=jsonPayload, headers=headers)
    
    resolvedNamesList = []

    if response.status_code == requests.codes.ok:    
        data_json = json.loads(response.text)
        rsnames_list = data_json['results'] 
        resolvedNamesList = get_resolved_names(rsnames_list, do_fuzzy_match, multi_match)
        #write_result(resolvedNamesList)
        status_code = 200
        message = "Success"
    else:
        status_code = 500
        message = "Error resolving names with OTL"

    return {'resolvedNames': resolvedNamesList, 'status_code': status_code, 'message': message}
 
#-------------------------------------------
def get_resolved_names(results, do_fuzzy_match, multi_match):
 	resolvedNameslist = []
 	
 	for element in results:
 		match_list = element['matches']
 		
 		for match_result in match_list:
 			namesList = {}
 			search_str = match_result['search_string']
 			match_str = match_result['matched_name']
 			match_type = match_result['is_approximate_match']
 			match_score = match_result['score']
 			ott_id = match_result['ot:ottId']
 			synonyms = match_result['synonyms']
 			if float(match_score) > 0.5:	     	
 				namesList['matched_name'] = match_str
 				namesList['search_string'] = search_str	 
 				namesList['match_type'] = 'Exact' if not(match_type) else 'Fuzzy'
 				namesList['synonyms'] = synonyms
 				namesList['taxon_id'] = ott_id
 				namesList['resolver_name'] = 'OT'	
 				resolvedNameslist.append(namesList)
 				if not(multi_match) and do_fuzzy_match:
 					break;
 	#print len(resolvedNameslist)
 	return resolvedNameslist

#---------------------------------
def create_sublists(lst, size=200):
	return [lst[i:i+size] for i in xrange(0, len(lst), size)]

#--------------------------------------------
def resolve_names_OT(inputNamesList):
    """Resolves scientific names using Open Tree of Life TNRS
    
	For example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.resolve_names_OT(["Formica polyctena", "Tetramorium caespitum","Carebara diversa"])
	>>> print result
	{"total_names": 3, "resolvedNames": [{"match_type": "Exact", "resolver_name": "OT", "matched_name": "Tetramorium caespitum", "search_string": "tetramorium caespitum", "synonyms": ["Tetramorium caespitum"], "taxon_id": 214421}, {"match_type": "Exact", "resolver_name": "OT", "matched_name": "Formica polyctena", "search_string": "formica polyctena", "synonyms": ["Formica polyctenum", "Formica polyctena"], "taxon_id": 815730}, {"match_type": "Exact", "resolver_name": "OT", "matched_name": "Carebara diversa", "search_string": "carebara diversa", "synonyms": ["Pheidologeton diversus", "Carebara diversus", "Carebara diversa"], "taxon_id": 842045}], "input_query": ["Formica polyctena", "Tetramorium caespitum", "Carebara diversa"], "service_url_doc": "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-3", "execution_time": "0.55", "status_code": 200, "message": "Success", "creation_time": "2017-06-26T14:24:17.800451"}

    :param inputNamesList: A list of scientific names to be resolved. 
    :type inputNamesList: A list of str. 
    
    :returns: A json formatted string -- with a list of dict objects as the value of the ``resolvedNames`` property. 

    """ 
    FuzzyMatch=True
    MultiMatch=False
    post=False
    list_size = 250
    final_result = []

    start_time = time.time()

    if len(inputNamesList) > list_size:
    	sublists = create_sublists(inputNamesList, list_size)
    	for sublst in sublists:
    		resolvedResult = resolve_sn_ot(sublst, FuzzyMatch, MultiMatch)
    		resolvedNameslst = resolvedResult['resolvedNames']
    		final_result.extend(resolvedNameslst)
    	status_code = resolvedResult['status_code']
    	message = resolvedResult['message']  
    else:
    	resolvedResult = resolve_sn_ot(inputNamesList, FuzzyMatch, MultiMatch)
    	final_result = resolvedResult['resolvedNames']
    	status_code = resolvedResult['status_code']
    	message = resolvedResult['message']

    if len(final_result) <= 0 and status_code != 500:
    	status_code = 204
        message = "Could not resolve any name" 

    end_time = time.time()
    result_len = len(final_result)
  
    service_documentation = "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-3"
    execution_time = "{:4.2f}".format(end_time-start_time)
    #service result creation time
    creation_time = datetime.datetime.now().isoformat()

    if post: 	    
     	return {'resolvedNames': final_result, 'creation_time': creation_time, 'execution_time': execution_time, 'total_names': result_len, 'status_code': status_code, "service_url_doc": service_documentation, 'input_query': inputNamesList , 'message': message}
    else: 
        return json.dumps({'resolvedNames': final_result, 'creation_time': creation_time, 'execution_time': execution_time, 'total_names': result_len, 'status_code': status_code, "service_url_doc": service_documentation, 'input_query': inputNamesList, 'message': message}) 

#-----------------------------------------------------------
def resolve_names_GNR(inputNamesList): 
    """Resolves scientific names using Global Names Resolver
    
	For example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.resolve_names_GNR(["Formica exsectoides","Formica pecefica", "Setophaga angilae"])
	>>> print result
	{"resolvedNames": [{"match_type": "Exact", "resolver_name": "GNR", "matched_name": "Formica exsectoides", "search_string": "Formica exsectoides", "synonyms": [], "taxon_id": "609781"}, {"match_type": "Fuzzy", "resolver_name": "GNR", "matched_name": "Formica pacifica", "search_string": "Formica pecefica", "synonyms": [], "taxon_id": "6876591"}, {"match_type": "Fuzzy", "resolver_name": "GNR", "matched_name": "Setophaga angelae", "search_string": "Setophaga angilae", "synonyms": [], "taxon_id": "24836501"}], "parameters": {"with_vernaculars": false, "best_match_only": true, "data_sources": [], "with_context": false, "header_only": false, "resolve_once": false, "preferred_data_sources": [], "with_canonical_ranks": false}, "execution_time": "0.70", "status_code": 200, "creation_time": "2017-06-26T14:28:02.414901", "total_names": 3, "input_query": ["Formica exsectoides", "Formica pecefica", "Setophaga angilae"], "service_url_doc": "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-4", "message": "Success"}

    :param inputNamesList: A list of scientific names to be resolved. 
    :type inputNamesList: A list of str. 
    
    :returns: A json formatted string -- with a list of dict objects as the value of the ``resolvedNames`` property. 

    """
    post=False
    start_time = time.time()
    api_friendly_list = make_api_friendly_list(inputNamesList)	
    final_result = resolve_sn_gnr(api_friendly_list, post)    
    end_time = time.time()
    execution_time = end_time-start_time

    #service result creation time
    creation_time = datetime.datetime.now().isoformat()
    final_result['creation_time'] = creation_time
    final_result['execution_time'] = "{:4.2f}".format(execution_time)
    final_result['total_names'] = len(final_result['resolvedNames'])
    final_result['input_query'] = inputNamesList

    if post: 	    
        return final_result
    else:
        return json.dumps(final_result)  

#------------------------------------------------------

