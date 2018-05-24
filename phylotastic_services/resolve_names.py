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
def resolve_sn_gnr(scNames, do_fuzzy_match, multi_match):
    if do_fuzzy_match:
       best_match = 'false'
    else:
       best_match = 'true'

    payload = {
        'names': scNames,
        'best_match_only': best_match
    }
    
    #encoded_payload = urllib.urlencode(payload)
    #response = requests.get(api_url, params=encoded_payload, headers=headers) 
    response = requests.post(api_url, data=payload)     

    resolvedNamesList = [] 
    data_json = json.loads(response.text)

    if response.status_code == requests.codes.ok:        
        rsnames_list = data_json['data']
        parameters_list = data_json['parameters']   
        for element in rsnames_list:
            mult_matches_list = []
            input_name = element['supplied_name_string']
            if 'results' not in element:
               continue
            match_list = element['results']
            for match in match_list:
                namesList = {}
                
                if float(match['score']) >= 0.75:
                   rsname = match['canonical_form']
       	           namesList['search_string'] = input_name
            	   namesList['matched_name'] =  rsname
            	   namesList['match_type'] = 'Exact' if match['match_type'] == 1 else 'Fuzzy'
                   namesList['data_source'] = match['data_source_title']      
            	   namesList['synonyms'] = []
                   namesList['match_score'] = match['score']  
            	   namesList['taxon_id'] = match['taxon_id']		
                   mult_matches_list.append(namesList)	
                if not(multi_match) and do_fuzzy_match: 
                   break

            if not do_fuzzy_match and match['match_type'] !=1:
               continue
            resolvedNamesList.append({'input_name': input_name, 'matched_results': mult_matches_list})
		
        statuscode = 200
        msg = "Success" 
    else:
        if 'message' in data_json:
           msg = "GNR Error: "+data_json['message']
        else:
           msg = "Error: Response error while resolving names with GNR"
        if 'status' in data_json:
           statuscode = data_json['status']
        
        statuscode = response.status_code   

    print resolvedNamesList
    return {'resolvedNames': resolvedNamesList, 'gnr_parameters': parameters_list, 'status_code': statuscode, 'message': msg}
        
#----------------------------------------------    

#Process Scientific Names List for GNR
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
                
#-----------------------------------------------------
#Process Scientific Names List for iPlant
def make_iplant_api_friendly_list(scNamesList):
    #process list for iPlant api    
    ListSize = len(scNamesList)    
    
    count = 0;
    TobeResolvedNames = ''
    
    for str_element in scNamesList:
        count += 1
        if(count != ListSize):
            str_element += ',' 
        TobeResolvedNames += str_element
    
    #print "List size:"+ str(ListSize)    
    return TobeResolvedNames


#~~~~~~~~~~~~~~~~~~~~ (iplantcollaborative-TNRS)~~~~~~~~~~~~~~~~~~~~~~~~~~~
#resolve scientific names using iplantcollaborative
def resolve_sn_iplant(scNames, do_fuzzy_match, multi_match):
    """
    Source: http://tnrs.iplantcollaborative.org/api.html
    """
    iplant_api_url = "http://tnrs.iplantc.org/tnrsm-svc/matchNames"

    if do_fuzzy_match:
       match_type = 'all'  #'all' retrieves all matches
    else:
       match_type = 'best' #'best' retrieves only the single best match for each name submitted

    payload = {
        'names': scNames,
        'retrieve': match_type
    }
    
    encoded_payload = urllib.urlencode(payload)
    response = requests.get(iplant_api_url, params=encoded_payload) 
    #print response.text
    
    resolvedNamesList = [] 
    data_json = json.loads(response.text)

    if response.status_code == requests.codes.ok:  
        rsnames_list = data_json['items']
        
        #get the group numbers
        group_list = []
        for element in rsnames_list:
            if int(element['group']) not in group_list: 
               group_list.append(int(element['group']))

        #find the multiple matches of the same item 
        for group in group_list:
            match_list = []
            for rsn in rsnames_list:
                if int(rsn['group']) == group:
                   match_list.append(rsn)
                
            mult_matches_list = []
            for matched_element in match_list:
                namesList = {} 
                input_name = matched_element['nameSubmitted']
                match_score = float(matched_element['scientificScore'])
                taxon_url = matched_element['url']
                if match_score >= 0.5:
                   rs_name = matched_element['nameScientific']
       	           namesList['search_string'] = input_name
                   namesList['matched_name'] =  rs_name
                   namesList['match_type'] = 'Exact' if match_score == 1 else 'Fuzzy'
                   namesList['data_source'] = "Tropicos - Missouri Botanical Garden"      
                   namesList['synonyms'] = []
                   namesList['match_score'] = match_score  
                   namesList['taxon_id'] = taxon_url[taxon_url.rfind("/")+1:len(taxon_url)]		
                   mult_matches_list.append(namesList)	
               
                if not(multi_match) and do_fuzzy_match:
                   break
               
            if not(do_fuzzy_match) and match_score != 1:
               continue
 
            resolvedNamesList.append({'input_name': input_name, 'matched_results': mult_matches_list})		

        statuscode = 200
        msg = "Success" 
    else:
        if 'message' in data_json:
           msg = "iPlantcollaborative Error: "+data_json['message']

        else:
           msg = "Error: Response error while resolving names with iPlantcollaborative"
        if 'status' in data_json:
           statuscode = data_json['status']
        
        statuscode = response.status_code   

    return {'resolvedNames': resolvedNamesList, 'status_code': statuscode, 'message': msg}
        
#----------------------------------------------    
                

#~~~~~~~~~~~~~~~~~~~~ (OpenTreeofLife-TNRS)~~~~~~~~~~~~~~~~~~~~~~~~~~~
def resolve_sn_ot(scNames, do_fuzzy_match, multi_match):
    opentree_api_url = 'https://api.opentreeoflife.org/v2/tnrs/match_names'
  
    payload = {
        'names': scNames,
 		'do_approximate_matching': do_fuzzy_match
    }
    jsonPayload = json.dumps(payload)

    try: 
       response = requests.post(opentree_api_url, data=jsonPayload, headers=headers)
    except requests.exceptions.ConnectionError:
       return {'resolvedNames': [],'status_code': 500, 'message': "Connection error with OpenTreeofLife API"}

    #----------------------------------------------
    #response = requests.post(opentree_api_url, data=jsonPayload, headers=headers)
    
    data_json = json.loads(response.text)

    resolvedNamesList = []

    if response.status_code == requests.codes.ok:    
        rsnames_list = data_json['results'] 
        resolvedNamesList = get_resolved_names(rsnames_list, do_fuzzy_match, multi_match)
        statuscode = 200
        msg = "Success"
    else:
        if 'message' in data_json:
           msg = "OToL TNRS Error: "+data_json['message']
        else:
           msg = "Error: Response error while resolving names with OToL TNRS"
        if 'status' in data_json:
           statuscode = data_json['status']
        
        statuscode = response.status_code   
        
    return {'resolvedNames': resolvedNamesList, 'status_code': statuscode, 'message': msg}
 
#-------------------------------------------
def get_resolved_names(results, do_fuzzy_match, multi_match):
 	resolvedNameslist = []
 	
 	for element in results:
 		input_name = element['id']
 		match_list = element['matches']
 		mult_matches_list = []
 		for match_result in match_list:
 			namesList = {}
 			search_str = match_result['search_string']
 			match_str = match_result['matched_name']
 			match_type = match_result['is_approximate_match']
 			match_score = match_result['score']
 			ott_id = match_result['ot:ottId']
 			synonyms = match_result['synonyms']
 			if float(match_score) >= 0.75:	     	
 				namesList['matched_name'] = match_str
 				namesList['search_string'] = search_str	 
 				namesList['match_type'] = 'Exact' if not(match_type) else 'Fuzzy'
 				namesList['match_score'] = match_score          
 				namesList['synonyms'] = synonyms
 				namesList['taxon_id'] = ott_id
 				namesList['data_source'] = "Open Tree of Life Reference Taxonomy"
 				mult_matches_list.append(namesList)	
 			if not(multi_match) and do_fuzzy_match: 
 				break

 		resolvedNameslist.append({'input_name': input_name, 'matched_results': mult_matches_list})

 	#print len(resolvedNameslist)
 	return resolvedNameslist

#---------------------------------
def create_sublists(lst, size=200):
	return [lst[i:i+size] for i in xrange(0, len(lst), size)]

#--------------------------------------------
def resolve_names_OT(inputNamesList, do_fuzzy_match, multi_match): 
    list_size = 250
    final_result = []

    start_time = time.time()
    
    status_code = 200
    message = "Success"

    if len(inputNamesList) > list_size:
    	sublists = create_sublists(inputNamesList, list_size)
    	for sublst in sublists:
    		resolvedResult = resolve_sn_ot(sublst, do_fuzzy_match, multi_match)
    		resolvedNameslst = resolvedResult['resolvedNames']
    		if resolvedResult['status_code'] != 200:
    			return {'status_code': resolvedResult['status_code'], 'message': resolvedResult['message']}
    		final_result.extend(resolvedNameslst)  
    else:
    	resolvedResult = resolve_sn_ot(inputNamesList, do_fuzzy_match, multi_match)
    	final_result = resolvedResult['resolvedNames']
    	status_code = resolvedResult['status_code']
    	message = resolvedResult['message']

    result_len = len(final_result)

    if result_len <= 0 and status_code == 200:
        message = "Could not resolve any name" 

    end_time = time.time()
    
    #service_documentation = "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-3"
    execution_time = float("{:4.2f}".format(end_time-start_time))
    #service result creation time
    creation_time = datetime.datetime.now().isoformat()
    meta_data = {'creation_time': creation_time, 'execution_time': execution_time, 'source_urls':["https://github.com/OpenTreeOfLife/opentree/wiki/Open-Tree-of-Life-APIs#tnrs"] }
#"service_documentation": service_documentation}

    #return {'resolvedNames': final_result, 'total_names': result_len, 'status_code': status_code, 'input_names': inputNamesList , 'message': message, 'meta_data': meta_data}
    return {'resolvedNames': final_result, 'total_names': result_len, 'status_code': status_code, 'message': message, 'meta_data': meta_data}

#--------------------------------------------
def resolve_names_OT(inputNamesList, do_fuzzy_match=False, multi_match=False):
    """Resolves scientific names using Open Tree of Life TNRS
    
	For example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.resolve_names_OT(["Formica polyctena", "Tetramorium caespitum","Carebara diversa"])
	>>> print result
	{"status_code": 200, "message": "Success", "meta_data": {"execution_time": 0.32, "creation_time": "2018-05-23T19:11:42.801871", "source_urls": ["https://github.com/OpenTreeOfLife/opentree/wiki/Open-Tree-of-Life-APIs#tnrs"]}, "total_names": 3, "resolvedNames": [{"matched_results": [{"data_source": "Open Tree of Life Reference Taxonomy", "match_type": "Exact", "match_score": 1.0, "matched_name": "Tetramorium caespitum", "search_string": "tetramorium caespitum", "synonyms": ["Tetramorium caespitum"], "taxon_id": 214421}], "input_name": "Tetramorium caespitum"}, {"matched_results": [{"data_source": "Open Tree of Life Reference Taxonomy", "match_type": "Exact", "match_score": 1.0, "matched_name": "Formica polyctena", "search_string": "formica polyctena", "synonyms": ["Formica polyctenum", "Formica polyctena"], "taxon_id": 815730}], "input_name": "Formica polyctena"}, {"matched_results": [{"data_source": "Open Tree of Life Reference Taxonomy", "match_type": "Exact", "match_score": 1.0, "matched_name": "Carebara diversa", "search_string": "carebara diversa", "synonyms": ["Pheidologeton diversus", "Carebara diversus", "Carebara diversa"], "taxon_id": 842045}], "input_name": "Carebara diversa"}]}

    :param inputNamesList: A list of scientific names to be resolved. 
    :type inputNamesList: A list of str. 
    :param do_fuzzy_match: A boolean value to specify whether to perform approximate string (a.k.a. "fuzzy") matching. By default, it is ``False``. To turn on "fuzzy" matching ``True`` must be used.
    :type do_fuzzy_match: boolean.
    :param multi_match: A boolean value to specify whether to return multiple match results when fuzzy matching is turned on. By default it is ``False``. If fuzzy matching is turned on and multiple_match is enabled (``True``), then it will return results of matches with score more than 0.75.
    :type multi_match: boolean.
    
    :returns: A json formatted string -- with a list of dict objects as the value of the ``resolvedNames`` property. 

    """ 
    list_size = 250
    final_result = []

    start_time = time.time()
    
    status_code = 200
    message = "Success"

    if len(inputNamesList) > list_size:
    	sublists = create_sublists(inputNamesList, list_size)
    	for sublst in sublists:
    		resolvedResult = resolve_sn_ot(sublst, do_fuzzy_match, multi_match)
    		resolvedNameslst = resolvedResult['resolvedNames']
    		if resolvedResult['status_code'] != 200:
    			return {'status_code': resolvedResult['status_code'], 'message': resolvedResult['message']}
    		final_result.extend(resolvedNameslst)  
    else:
    	resolvedResult = resolve_sn_ot(inputNamesList, do_fuzzy_match, multi_match)
    	final_result = resolvedResult['resolvedNames']
    	status_code = resolvedResult['status_code']
    	message = resolvedResult['message']

    result_len = len(final_result)

    if result_len <= 0 and status_code == 200:
        message = "Could not resolve any name" 

    end_time = time.time()
    
    #service_documentation = "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-3"
    execution_time = float("{:4.2f}".format(end_time-start_time))
    #service result creation time
    creation_time = datetime.datetime.now().isoformat()
    meta_data = {'creation_time': creation_time, 'execution_time': execution_time, 'source_urls':["https://github.com/OpenTreeOfLife/opentree/wiki/Open-Tree-of-Life-APIs#tnrs"] }
#"service_documentation": service_documentation}

    #return {'resolvedNames': final_result, 'total_names': result_len, 'status_code': status_code, 'input_names': inputNamesList , 'message': message, 'meta_data': meta_data}
    return json.dumps({'resolvedNames': final_result, 'total_names': result_len, 'status_code': status_code, 'message': message, 'meta_data': meta_data})

#-----------------------------------------------------------
def resolve_names_GNR(inputNamesList, do_fuzzy_match=False, multi_match=False): 
    """Resolves scientific names using Global Names Resolver
    
	For example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.resolve_names_GNR(["Formica exsectoides","Formica pecefica", "Setophaga angilae"], True)
	>>> print result
	{"resolvedNames": [{"matched_results": [{"data_source": "NCBI", "match_type": "Exact", "match_score": 0.988, "matched_name": "Formica exsectoides", "search_string": "Formica exsectoides", "synonyms": [], "taxon_id": "609781"}], "input_name": "Formica exsectoides"}, {"matched_results": [{"data_source": "Catalogue of Life", "match_type": "Fuzzy", "match_score": 0.75, "matched_name": "Formica pacifica", "search_string": "Formica pecefica", "synonyms": [], "taxon_id": "2f41fe085d8ff5d5bb75e520d0a692de"}], "input_name": "Formica pecefica"}, {"matched_results": [{"data_source": "Catalogue of Life", "match_type": "Fuzzy", "match_score": 0.75, "matched_name": "Setophaga angelae", "search_string": "Setophaga angilae", "synonyms": [], "taxon_id": "70b0dd5edac3927169524396759bbbfa"}], "input_name": "Setophaga angilae"}], "status_code": 200, "meta_data": {"execution_time": 0.52, "creation_time": "2018-05-23T19:14:16.947898", "source_urls": ["http://resolver.globalnames.org/"]}, "total_names": 3, "gnr_parameters": {"with_vernaculars": false, "best_match_only": false, "data_sources": [], "with_context": false, "header_only": false, "resolve_once": false, "preferred_data_sources": [], "with_canonical_ranks": false}, "message": "Success"}

    :param inputNamesList: A list of scientific names to be resolved. 
    :type inputNamesList: A list of str. 
    :param do_fuzzy_match: A boolean value to specify whether to perform approximate string (a.k.a. "fuzzy") matching. By default, it is ``False``. To turn on "fuzzy" matching ``True`` must be used.
    :type do_fuzzy_match: boolean.
    :param multi_match: A boolean value to specify whether to return multiple match results when fuzzy matching is turned on. By default it is ``False``. If fuzzy matching is turned on and multiple_match is enabled (``True``), then it will return results of matches with score more than 0.75.
    :type multi_match: boolean.

    :returns: A json formatted string -- with a list of dict objects as the value of the ``resolvedNames`` property. 

    """
    
    start_time = time.time()
    api_friendly_list = make_api_friendly_list(inputNamesList)	
    final_result = resolve_sn_gnr(api_friendly_list, do_fuzzy_match, multi_match)    
    end_time = time.time()
    execution_time = end_time-start_time

    result_len = len(final_result['resolvedNames'])
    if result_len <= 0 and final_result['status_code'] == 200:
        final_result['message'] = "Could not resolve any name"

    #service_documentation = "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-4"
    #service result creation time
    creation_time = datetime.datetime.now().isoformat()
    meta_data = {'creation_time': creation_time, 'execution_time': float("{:4.2f}".format(execution_time)), 'source_urls': ["http://resolver.globalnames.org/"] }
#"service_documentation": service_documentation}
    final_result['meta_data'] = meta_data
    final_result['total_names'] = result_len
    #final_result['input_names'] = inputNamesList
    
    return json.dumps(final_result)

#------------------------------------------------------
def resolve_names_iPlant(inputNamesList, do_fuzzy_match=False, multi_match=False): 
    """Resolves scientific names using iplantCollaborative TNRS
    
	For example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.resolve_names_iPlant(["Acanthophyllum albidum","Acanthostachys pitcairnioides","Acanthostyles buniifolius"], True, False)
	>>> print result
	{"status_code": 200, "message": "Success", "meta_data": {"execution_time": 0.46, "creation_time": "2018-05-23T19:05:45.652250", "source_urls": ["http://tnrs.iplantcollaborative.org"]}, "total_names": 3, "resolvedNames": [{"matched_results": [{"data_source": "Tropicos - Missouri Botanical Garden", "match_type": "Exact", "match_score": 1.0, "matched_name": "Acanthophyllum albidum", "search_string": "Acanthophyllum albidum", "synonyms": [], "taxon_id": "6302165"}], "input_name": "Acanthophyllum albidum"}, {"matched_results": [{"data_source": "Tropicos - Missouri Botanical Garden", "match_type": "Exact", "match_score": 1.0, "matched_name": "Acanthostachys pitcairnioides", "search_string": "Acanthostachys pitcairnioides", "synonyms": [], "taxon_id": "50038733"}], "input_name": "Acanthostachys pitcairnioides"}, {"matched_results": [{"data_source": "Tropicos - Missouri Botanical Garden", "match_type": "Exact", "match_score": 1.0, "matched_name": "Acanthostyles buniifolius", "search_string": "Acanthostyles buniifolius", "synonyms": [], "taxon_id": "2712077"}], "input_name": "Acanthostyles buniifolius"}]}

    :param inputNamesList: A list of scientific names to be resolved. 
    :type inputNamesList: A list of str. 
    :param do_fuzzy_match: A boolean value to specify whether to perform approximate string (a.k.a. "fuzzy") matching. By default, it is ``False``. To turn on "fuzzy" matching ``True`` must be used.
    :type do_fuzzy_match: boolean.
    :param multi_match: A boolean value to specify whether to return multiple match results when fuzzy matching is turned on. By default it is false. If fuzzy matching is turned on and multiple_match is enabled (``True``), then the service will return results of matches with score more than 0.50.
    :type multi_match: boolean.

    :returns: A json formatted string -- with a list of dict objects as the value of the ``resolvedNames`` property. 

    """
    start_time = time.time()
    api_friendly_list = make_iplant_api_friendly_list(inputNamesList)	
    final_result = resolve_sn_iplant(api_friendly_list, do_fuzzy_match, multi_match)    
    end_time = time.time()
    execution_time = end_time-start_time

    result_len = len(final_result['resolvedNames'])
    if result_len <= 0 and final_result['status_code'] == 200:
        final_result['message'] = "Could not resolve any name"

    #service_documentation = ""
    #service result creation time
    creation_time = datetime.datetime.now().isoformat()
    meta_data = {'creation_time': creation_time, 'execution_time': float("{:4.2f}".format(execution_time)), 'source_urls': ["http://tnrs.iplantcollaborative.org"] }
#"service_documentation": service_documentation}
    final_result['meta_data'] = meta_data
    final_result['total_names'] = result_len
    #final_result['input_names'] = inputNamesList
    
    return json.dumps(final_result)
