"""
**study_tree** Module is for getting phylogenetic tree metadata(supporting studies) or to compare trees or to retrieve tree chronogram 
"""
import json
import datetime
import dendropy
from dendropy.calculate import treecompare
import time
import requests

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
headers = {'content-type': 'application/json'}
opentree_base_url = "https://api.opentreeoflife.org/v3/"

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def compare_trees(tree1, tree2):
 	"""Compares two phylogenetic trees using Robinson-Foulds distance.
    
	Example:
	
	>>> import phylotastic_services
	>>> result = phylotastic_services.compare_trees(tree1="(((((((EU368025_Uncult_marine_euk_FS14JA72_30Mar05_5m:0.00329,EU368020_Uncult_marine_euk_FS04GA95_01Aug05_5m:-0.00002):0.00002,EU368013_Uncult_marine_euk_FS01D014_01Aug05_65m:-0.00002):0.00010,(EU368034_Uncult_marine_euk_OC413NSS_Q007_15m:-0.00000,(EU368007_Uncult_marine_euk_FS01B026_30Mar05_5m:-0.00001,EU368004_Uncult_marine_euk_FS01AA94_01Aug05_5m:0.00328):0.00000):0.00317):0.00725,(EU368005_Uncult_marine_euk_FS01B033_30Mar05_5m:-0.00002,(EF172850_Uncult_euk_SSRPB47:-0.00003,EU368022_Uncult_marine_euk_FS04H169_01Aug05_89m:0.00166):0.00002):0.00597):0.00202,((DQ060523_Uncult_marine_euk_NOR46.29:0.01559,(HQ868826_Uncult_euk_SHAX1073:0.00155,EU368038_Uncult_marine_euk_EN351CTD040_4mN11:0.00172):0.00429):0.00017,(EU368023_Uncult_marine_euk_FS04H153_01Aug05_89m:0.00504,(DQ222879_Uncult_photo_euk_RA000907.18:0.00166,HM858468_Uncult_marine_euk_MO.011.5m.00036:-0.00003):0.00152):0.00566):0.00662):0.00941,(HQ868882_Uncult_euk_SHAX1135:0.00170,HQ868810_Uncult_euk_SHAX1056:-0.00007):0.02449):0.00648,(EU368021_Uncult_marine_euk_FS04GA46_01Aug05_5m:0.02285,(HQ869075_Uncult_euk_SHAX587:0.00000,HQ869035_Uncult_euk_SHAX540:0.00000):0.04720):0.01029,HQ156863_Uncult_marine_ciliate_170609_08:0.17059);", tree2="((HQ869075_Uncult_euk_SHAX587:0.00000,HQ869035_Uncult_euk_SHAX540:0.00000):0.04484,(EU368021_Uncult_marine_euk_FS04GA46_01Aug05_5m:0.02285,(((((EU368005_Uncult_marine_euk_FS01B033_30Mar05_5m:-0.00002,(EF172850_Uncult_euk_SSRPB47:-0.00003,EU368022_Uncult_marine_euk_FS04H169_01Aug05_89m:0.00166):0.00002):0.00597,(((EU368025_Uncult_marine_euk_FS14JA72_30Mar05_5m:0.00329,EU368020_Uncult_marine_euk_FS04GA95_01Aug05_5m:-0.00002):0.00002,EU368013_Uncult_marine_euk_FS01D014_01Aug05_65m:-0.00002):0.00010,(EU368034_Uncult_marine_euk_OC413NSS_Q007_15m:-0.00000,(EU368007_Uncult_marine_euk_FS01B026_30Mar05_5m:-0.00001,EU368004_Uncult_marine_euk_FS01AA94_01Aug05_5m:0.00328):0.00000):0.00317):0.00725):0.00202,((DQ060523_Uncult_marine_euk_NOR46.29:0.01559,(HQ868826_Uncult_euk_SHAX1073:0.00155,EU368038_Uncult_marine_euk_EN351CTD040_4mN11:0.00172):0.00429):0.00017,(EU368023_Uncult_marine_euk_FS04H153_01Aug05_89m:0.00504,(DQ222879_Uncult_photo_euk_RA000907.18:0.00166,HM858468_Uncult_marine_euk_MO.011.5m.00036:-0.00003):0.00152):0.00566):0.00662):0.00941,(HQ868882_Uncult_euk_SHAX1135:0.00170,HQ868810_Uncult_euk_SHAX1056:-0.00007):0.02449):0.00648,HQ156863_Uncult_marine_ciliate_170609_08:0.17059):0.01029):0.00236);")
	>>> print result
	{"status_code": 200, "message": "Success", "meta_data": {"execution_time": 0.02, "creation_time": "2018-06-10T17:47:17.668300", "source_urls": ["http://dendropy.org/library/treecompare.html#module-dendropy.calculate.treecompare"]}, "are_same_tree": true}

    :param tree1: First phylogenetic tree in newick format. 
    :type tree1: string.
    :param tree2: Second phylogenetic tree in newick format. 
    :type tree2: string.  
    :returns: A json formatted string -- with a boolean value in ``are_same_tree`` property indicating whether two trees are same or not. 

    """
 	response = {}
 	start_time = time.time()
 	try:	
 		tns = dendropy.TaxonNamespace() 	
 	
 		tree_obj1 = dendropy.Tree.get(data=tree1, schema="newick",taxon_namespace=tns)
 		tree_obj2 = dendropy.Tree.get(data=tree2, schema="newick",taxon_namespace=tns)

 		tree_obj1.encode_bipartitions()
 		tree_obj2.encode_bipartitions()

 		#-----------------------------------------------------------
 		#This method returns the symmetric distance between two trees. 
 		#The symmetric distance between two trees is the sum of the number of  splits found in one of the trees but not the other. 
 		#It is common to see this statistic called the Robinson-Foulds distance

 		areSame = True if treecompare.symmetric_difference(tree_obj1, tree_obj2) == 0 else False
 		status = 200
 		message = "Success"
 		response['are_same_tree'] = areSame
 
 	except Exception, e:
 		if "Incomplete or improperly-terminated tree statement" in str(e): #invalid: "((A,B),C,D));"  valid: ((A,B),(C,D)); 
 			message = "NewickReaderIncompleteTreeStatementError: " + str(e)
 	 		status = 400
 		elif "Unbalanced parentheses at tree statement" in str(e):  #invalid: "((A,B),(C,D);"  valid: ((A,B),(C,D)); 
 			message = "NewickReaderMalformedStatementError: "+str(e) 
 	 		status = 400
 		elif "Multiple occurrences of the same taxa" in str(e): #invalid: "((A,B),(C,C));"  valid: ((A,B),(C,D));
 			message = "NewickReaderDuplicateTaxonError: "+str(e)
 	 		status = 400
 		elif "Unexpected end of stream" in str(e): # invalid: "((A,B),(C,D))"  valid: ((A,B),(C,D));
 			message = "UnexpectedEndOfStreamError: "+str(e)
 	 		status = 400
 		else:
 			message = "Error: Failed to compare trees. "+str(e)
 	 		status = 500
 	 	
 	response['status_code'] = status
 	response['message'] = message

 	end_time = time.time()
 	execution_time = end_time-start_time
    #service result creation time
 	creation_time = datetime.datetime.now().isoformat()
 	meta_data = {'creation_time': creation_time, 'execution_time': float('{:4.2f}'.format(execution_time)), 'source_urls':["http://dendropy.org/library/treecompare.html#module-dendropy.calculate.treecompare"] }

 	response['meta_data'] = meta_data
 	print response
 	return response


#-------------------------------------------------------
#~~~~~~~~~~~~~~~~~~~~ (OpenTree-tree_of_life)~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
def get_study_ids(ottid_list):
    opentree_method_url = opentree_base_url + "tree_of_life/induced_subtree"
    
    payload = {
        'ott_ids': ottid_list	
    }
    
    jsonPayload = json.dumps(payload)
    
    response = requests.post(opentree_method_url, data=jsonPayload, headers=headers)
    
    studyid_result = {}

    if response.status_code == requests.codes.ok:    
        result_data_json = json.loads(response.text)
        studyid_result['study_ids'] = result_data_json['supporting_studies']
        studyid_result['message'] =  "Success"
     	studyid_result['status_code'] = 200
    else:    
        studyid_result['message'] =  "Error: getting study ids from OpenTree"
     	studyid_result['status_code'] = 500

    return studyid_result

#------------------------(OpenTree-studies)------------------------------
def get_study_info(studyid):
    opentree_method_url = opentree_base_url + "studies/find_studies"
    
    payload = {
        'property': 'ot:studyId',
        'value': studyid,
        'verbose': True	
    }
    
    jsonPayload = json.dumps(payload)
    
    response = requests.post(opentree_method_url, data=jsonPayload, headers=headers)
    
    studyinfo_result = {}

    if response.status_code == requests.codes.ok:    
        result_data_json = json.loads(response.text)
        if (len(result_data_json['matched_studies']) == 0):
           studyinfo_result['message'] =  "No matching study found"
     	   studyinfo_result['status_code'] = 204
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
        studyinfo_result['message'] =  "Error: getting study info from OpenTree"
     	studyinfo_result['status_code'] = 500

    return studyinfo_result

#----------------------------------------------------
def get_studies(studyid_list):
    studies_list = []
    for studyid in studyid_list:
        study_info = get_study_info(studyid)
        if study_info['status_code'] == 200:
           #delete status keys from dictionary 
           del study_info['status_code']
           del study_info['message']
           studies_list.append(study_info)
    
    return studies_list

#----------------------------------------------------
def get_studies_from_ids(id_list, is_ottid=True, post=False):
    start_time = time.time()
    studies_info = {}
    if is_ottid: #check whether the id_list is a list of ott ids or not
       study_id_list_json = get_study_ids(id_list)
       if study_id_list_json['status_code'] == 200:
          study_id_list = study_id_list_json['study_ids']
          studies_info['studies'] = get_studies(study_id_list) 
          studies_info['message'] = "Success"
          studies_info['status_code'] = 200
       else:
          studies_info['studies'] = []
          studies_info['message'] = study_id_list_json['message']
          studies_info['status_code'] = study_id_list_json['status_code']
    else: #when study ids are given directly
       study_list = get_studies(id_list)
       studies_info['studies'] = study_list  
       studies_info['message'] = "Success"
       studies_info['status_code'] = 204 if (len(study_list) == 0) else 200

    end_time = time.time()
    execution_time = end_time-start_time
    studies_info['execution_time'] = float('{:4.2f}'.format(execution_time))

    if post:
       return studies_info
    else:
       return json.dumps(studies_info)

#-------------------(OpenTree-TNRS)-----------------------------
def get_ott_ids(taxa, context=None):
    opentree_method_url = opentree_base_url + "tnrs/match_names"
    
    payload = {
        'names': taxa
    }
    if context is not None:
       payload['context_name'] = context

    jsonPayload = json.dumps(payload)
   
    response = requests.post(opentree_method_url, data=jsonPayload, headers=headers)
    
    ott_id_list = []
    ott_id_result = {}

    if response.status_code == requests.codes.ok:    
        result_data_json = json.loads(response.text)
        result_list = result_data_json['results'] 
        for result in result_list:
            match_list = result['matches']
            for match in match_list:
                if float(match['score']) >= 0.7:
                   ott_id_list.append(match['taxon']['ott_id'])
                   break

        ott_id_result['ott_ids'] = ott_id_list	
        ott_id_result['status_code'] = 200
        ott_id_result['message'] = "Success"
    else:
        ott_id_result['ott_ids'] = ott_id_list	
        ott_id_result['status_code'] = 500
        ott_id_result['message'] = "Error: getting ott ids from OpenTree"
    
    return ott_id_result

#----------------------------------------------------------
def get_studies_tree(taxa):
    """Gets supporting studies information from Open Tree of Life for a phylogenetic tree retrieved using a list of taxa.
    
    Example:
	
    >>> import phylotastic_services
    >>> result = phylotastic_services.get_studies_tree(taxa=["Setophaga striata", "Setophaga magnolia", "Setophaga angelae", "Setophaga plumbea", "Setophaga virens"])
    >>> print result
    {"execution_time": 2.07, "status_code": 200, "message": "Success", "studies": [{"PublicationYear": 2010, "FocalCladeTaxonName": "Parulidae", "Publication": "Lovette, Irby J., Jorge L. P\u00e9rez-Em\u00e1n, John P. Sullivan, Richard C. Banks, Isabella Fiorentino, Sergio C\u00f3rdoba-C\u00f3rdoba, Mar\u00eda Echeverry-Galvis, F. Keith Barker, Kevin J. Burns, John Klicka, Scott M. Lanyon, Eldredge Bermingham. 2010. A comprehensive multilocus phylogeny for the wood-warblers and a revised classification of the Parulidae (Aves). Molecular Phylogenetics and Evolution 57 (2): 753-770.", "CandidateTreeForSynthesis": "tree6024", "PublicationDOI": "http://dx.doi.org/10.1016/j.ympev.2010.07.018", "DataRepository": "", "Curator": "Joseph W. Brown", "PublicationIdentifier": "pg_2591"}, {"PublicationYear": 2015, "FocalCladeTaxonName": "Passeriformes", "Publication": "Barker, F. Keith, Kevin J. Burns, John Klicka, Scott M. Lanyon, Irby J. Lovette. 2015. New insights into New World biogeography: An integrated view from the phylogeny of blackbirds, cardinals, sparrows, tanagers, warblers, and allies. The Auk 132 (2): 333-348.", "CandidateTreeForSynthesis": "tree1", "PublicationDOI": "http://dx.doi.org/10.1642/auk-14-110.1", "DataRepository": "http://datadryad.org/resource/doi:10.5061/dryad.pb787", "Curator": "Joseph W. Brown", "PublicationIdentifier": "ot_770"}]}

    :param taxa: A list of taxa (of a phylogenetic tree) for which to supporting studies. 
    :type taxa: A list of strings.  
    :returns: A json formatted string -- with a list of species objects containing links to EOL. 

    """
    context=None
    post=False	 	
    start_time = time.time()
    ottidlist_json = get_ott_ids(taxa, context)
    studies_info = {}
    if ottidlist_json['status_code'] == 500:    
        final_result = ottidlist_json   
    else:
        study_id_list_json = get_study_ids(ottidlist_json['ott_ids'])
        if study_id_list_json['status_code'] == 200:
           studies_info['studies'] = get_studies(study_id_list_json['study_ids'])
           studies_info['message'] = "Success"
           studies_info['status_code'] = 200 
        else:
           studies_info['studies'] = []
           studies_info['message'] = study_id_list_json['message']
           studies_info['status_code'] = study_id_list_json['status_code']

        final_result = studies_info
    
    end_time = time.time()
    execution_time = end_time-start_time
    final_result['execution_time'] = float('{:4.2f}'.format(execution_time))

    if post:
       return final_result
    else:
       return json.dumps(final_result)
'''

#-------------------------------------------------
def get_chronogram_tree(tree=None):
 	"""Gets chronogram of a phylogenetic tree using Phylotastic datelife.
    
    Example:
	
    >>> import phylotastic_services
    >>> result = phylotastic_services.get_chronogram_tree(tree="(((((Canis lupus pallipes,Melursus ursinus)Caniformia,((Panthera tigris,Panthera pardus)Panthera,Herpestes fuscus))Carnivora,(Macaca mulatta,Homo sapiens)Catarrhini)Boreoeutheria,Elephas maximus)Eutheria,Haliastur indus)Amniota;")
    >>> print result
    {"execution_time": "4.27", "status_code": 200, "creation_time": "2017-07-03T11:51:53.384258", "scaled_tree": "((((Homo sapiens:29.126382,Macaca mulatta:29.126382):69.773618,(((Panthera pardus:6.4,Panthera tigris:6.4):34.300001,Herpestes fuscus:40.700001):24.199999,(Canis lupus pallipes:16.775,Melursus ursinus:16.775):48.125):34):10.65,Elephas maximus:109.55):17.078571,Haliastur indus:126.628571);", "input_tree": "(((((Canis lupus pallipes,Melursus ursinus)Caniformia,((Panthera tigris,Panthera pardus)Panthera,Herpestes fuscus))Carnivora,(Macaca mulatta,Homo sapiens)Catarrhini)Boreoeutheria,Elephas maximus)Eutheria,Haliastur indus)Amniota;", "message": "Success", "service_documentation": "https://github.com/phylotastic/phylo_services_docs/blob/master/ServiceDescription/PhyloServicesDescription.md#web-service-20"}

    :param tree: A phylogenetic tree in newick format. 
    :type tree: string.  
    :returns: A json formatted string -- with a newick formatted tree including branch lengths as the value of the ``scaled_tree`` property. 

    """
 	datelife_url = "http://phylo.cs.nmsu.edu:5009/phylotastic_ws/sc/scale"
    
 	if tree is None:
 		return json.dumps({"status": 500, "message": "No Tree provided as input"})
 
 	payload = {
        'newick': tree
    }

 	jsonPayload = json.dumps(payload)
   
 	response = requests.post(datelife_url, data=jsonPayload, headers=headers)
    
 	if response.status_code == requests.codes.ok:
 		final_result = response.text
 	else:	  
 		final_result = json.dumps({"status": 500, "message": "Unable to connect to datelife service"})

 	return final_result

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#if __name__ == '__main__':
	#taxalist = ["Setophaga striata", "Setophaga magnolia", "Setophaga angelae", "Setophaga plumbea", "Setophaga virens"]
	#print get_studies_tree(taxalist)
    #print get_chronogram_tree("(((((Canis lupus pallipes,Melursus ursinus)Caniformia,((Panthera tigris,Panthera pardus)Panthera,Herpestes fuscus))Carnivora,(Macaca mulatta,Homo sapiens)Catarrhini)Boreoeutheria,Elephas maximus)Eutheria,Haliastur indus)Amniota;")
