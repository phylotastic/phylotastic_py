"""
**list_species** Module is for manipulating (insert into, update on or delete from list server) a list of species 
"""
import json
import requests
import time
import datetime 
import urllib

#----------------------------------------------
base_url = "http://phylo.cs.nmsu.edu:5007/phylotastic_ws/sls" 
headers = {'content-type': 'application/json'}
#scientific_name_authorship(str.)    authorship of the scientific name of the species
#----------------------------------------------
class Species:
    """
    **Species** class is used to create an instance of a species. A species instance
    consists of data about a particular species.

 	**Species** *properties* are described below.

     .. table::

         ================================   ==============================================
         PROPERTY(type)                     DESCRIPTION
         ================================   ==============================================
         scientific_name(str.)               scientific name of the species
         vernacular_name(str.)               vernacular name of the species
         scientific_name_authorship(str.)    authorship of the scientific name of the species
         family(str.)                        the taxonomic rank family where the species belongs to
         order(str.)                         the taxonomic rank order where the species belongs to
         phylum(str.)                        the taxonomic rank phylum where the species belongs to
         nomenclature_code(str.)             he nomenclatural code of the species
         ================================   ==============================================

    :returns: a **Species** object which represents a species.

    **Example:**

    ::

        species_obj1=Species("Acer ginnala", "Amur maple", "Maxim.", "Aceraceae","Sapindales", "Streptophyta", "ICN") #creates a species object
    """
    def __init__(self, Sc_name, Vn_name, Sc_name_author, Family, Order, Phylum, Nm_code):
        self.scientific_name = Sc_name
        self.vernacular_name = Vn_name
        self.scientific_name_authorship = Sc_name_author 
        self.family = Family
        self.order = Order
        self.phylum = Phylum
        self.nomenclature_code = Nm_code

    def reprJSON(self):
        return dict(scientific_name=self.scientific_name, vernacular_name=self.vernacular_name, scientific_name_authorship=self.scientific_name_authorship, family=self.family, order=self.order,phylum=self.phylum, nomenclature_code=self.nomenclature_code)
			
#--------------------------------------------- 
class List:
    """
    **List** class is used to store information of a list. A list
    consists of a collection of Species objects and metadata about the list.

 	**List** *properties* are described below.

     .. table::

         ========================  ==============================================
         PROPERTY(type)            DESCRIPTION
         ========================  ==============================================
         title(str.)               title of the new list
         description(str.)         description of the new list
         author(str.)              a list of names of the authors who prepared the new list
         date_published(str.)      date when the new list is being posted (format: mm-dd-yyyy)
         curator(str.)             name of the curator of the new list
         curation_date(str.)       date when the new list is being curated (format: mm-dd-yyyy)
         source(str.)              source of the new list (url, publication)
         keywords(str.)            keywords related to the new list
         focal_clade(str.)         focal_clade of the new list
         extra_info(str.)          extra information about the new list
         origin(str.)              the origin from where the new list is being posted. (Permitted values: "script" or "webapp" or "mobileapp")
         is_public(bool.)          true if the new list posted can be viewed by public. Otherwise false
         species_list(obj)         a list of species objects  
         ========================  ==============================================

    :returns: a **List** object which represents a new list.

    **Example:**

    ::

        species_obj1=Species("Acer ginnala", "Amur maple", "Maxim.", "Aceraceae","Sapindales", "Streptophyta", "ICN") #creates a species object
        species_list = [species_obj1] # create a list of species objects
        list_obj = List("Illinois Invasive Plants", "This list contains the invasive species, with their Family and Order", ["Invasive.org  Center for Invasive Species and Ecosystem Health"], "06-25-2017", "HD Laughinghouse", "2-25-2016", "http://www.invasive.org/species/list.cfm?id=152", ["Plants", " invasive species", " Illinois"], "Embryophyta", "", "script", True, species_list) #create a list object
    """

    def __init__(self, title=None, description=None, author=None, date_published=None, curator=None, curation_date=None, source=None, keywords=None, focal_clade=None, extra_info=None, origin=None, is_public=None, species_list=None):
        self.title = title
        self.description = description
        self.author = author 
        self.date_published = date_published
        self.curator = curator
        self.curation_date = curation_date
        self.source = source
        self.keywords = keywords
        self.focal_clade = focal_clade
        self.extra_info = extra_info
        self.origin = origin
        self.is_public = is_public
        self.list_species = species_list

    def reprJSON(self):
 		list_dict = {}
 		if self.title is not None:
 			list_dict['list_title'] = self.title
 		if self.description is not None:
 			list_dict['list_description'] = self.description
 		if self.author is not None:
 			list_dict['list_author'] = self.author
 		if self.date_published is not None:
 			list_dict['list_date_published'] = self.date_published
 		if self.curator is not None:
 			list_dict['list_curator'] = self.curator
 		if self.curation_date is not None:
 			list_dict['list_curation_date'] = self.curation_date
 		if self.source is not None:
 			list_dict['list_source'] = self.source
 		if self.keywords is not None:
 			list_dict['list_keywords'] = self.keywords
 		if self.focal_clade is not None:
 			list_dict['list_focal_clade'] = self.focal_clade
 		if self.extra_info is not None:
 			list_dict['list_extra_info'] = self.extra_info
 		if self.extra_info is not None:
 			list_dict['list_origin'] = self.origin
 		if self.is_public is not None:
 			list_dict['is_list_public'] = self.is_public
 		if self.list_species is not None:
 			list_dict['list_species'] = self.list_species 

 		return list_dict

#----------------------------------------------------
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)

#-------------------------------------------
def insert_list_info(userId, listObj):
	"""Inserts a new list of species into the species list server.

	Example:

	>>> import phylotastic_services
	>>> species_obj1 = Species("Acer ginnala", "Amur maple", "Maxim.", "Aceraceae","Sapindales", "Streptophyta", "ICN")
	>>> species_list1 = [species_obj1]
	>>> list_obj = List("Illinois Invasive Plants", "This list contains the invasive species, with their Family and Order", ["Invasive.org  Center for Invasive Species and Ecosystem Health"], "06-25-2017", "HD Laughinghouse", "2-25-2016", "http://www.invasive.org/species/list.cfm?id=152", ["Plants", " invasive species", " Illinois"], "Embryophyta", "", "script", True, species_list1)
	>>> result = phylotastic_services.insert_list_info("abusalehmdtayeen@gmail.com", list_obj)
	>>> print result
	{"status_code": 200, "message": "Success", "list_id": 57}

	:param userId: Unique id (a valid gmail address) of a user. 
	:type userId: string.
	:param listObj: An instance of the **List** class. 
	:type listObj: object.
  
	:returns: A json formatted string -- with an integer of the list created as a value of the ``list_id`` property. 
	"""	
 	method = "/insert_list"
 	api_url = base_url + method
    
 	payload_data = {
 		'user_id': userId,
 		'list': listObj.reprJSON()
 	}
 	jsonPayload = json.dumps(payload_data, cls=ComplexEncoder)
    
 	response = requests.post(api_url, data=jsonPayload, headers=headers)
 	
 	if response.status_code == requests.codes.ok:    
 		return response.text
 	else:
 		return json.dumps({"status_code": 500, "message": "Error connecting with species list server"})

#-----------------------------------------------
def update_list_metadata(userId, listId, listObj, accessToken):
	"""Updates metadata of an existing list in the species list server.

	Example:

	>>> import phylotastic_services
	>>> list_obj = List(description="This list contains the invasive species", is_public=False)
 	>>> result = phylotastic_services.update_list_metadata("abusalehmdtayeen@gmail.com", 57, list_obj, "ya29.Glt8BAvKKpEsU165zpbMEEoAGZOXh_qqSVln8Rsc_BTPLtQjURNUwbd7Dv6mzIvG6A6DJjgC3fyv9uIJ3wkH_9Rbu4W7zXvyNEu9Y-T2FrdXOiabiSEngGbBl19c")
	>>> print result
	{"user_id": "abusalehmdtayeen@gmail.com", "date_modified": "2017-07-03T19:55:46.430503", "status_code": 200, "modified_content": {"list_description": "This list contains the invasive species", "is_list_public": false}, "list_id": 57, "list_title": "Illinois Invasive Plants", "message": "Success"}

	:param userId: Unique id (a valid gmail address) of a user. 
	:type userId: string.
	:param listId: Unique id of the list that needs to be modified. 
	:type listId: integer.
	:param listObj: An instance of the **List** class. 
	:type listObj: object.
	:param accessToken: Access token for the user with userId (valid gmail address). 
	:type accessToken: string.  

	:returns: A json formatted string -- with modified list object as a value of the ``modified_content`` property. 
	"""		 	
 	method = "/update_list"
 	api_url = base_url + method
    
 	payload_data = {
 		'user_id': userId,
 		'list_id': listId,
 		'access_token': accessToken,
 		'list': listObj.reprJSON()
 	}
 	jsonPayload = json.dumps(payload_data, cls=ComplexEncoder)
    
 	response = requests.post(api_url, data=jsonPayload, headers=headers)
    
 	if response.status_code == requests.codes.ok:    
 		return response.text
 	else:
 		return json.dumps({"status_code": 500, "message": "Error connecting with species list server"})

#-----------------------------------------------
def update_list_data(userId, listId, speciesList, accessToken):
	"""Updates data/content of an existing list in the species list server.

	Example:

	>>> import phylotastic_services
	>>> species_obj1 = Species("Acer ginnala", "Amur maple", "Maxim.", "Aceraceae","Sapindales", "Streptophyta", "ICN")
	>>> species_obj2 = Species("Achyranthes japonica", "Japanses chaff flower", "(Miq.) Nakal", "Amaranthaceae", "Caryophyllales", "Streptophyta", "ICN")
	>>> species_list2 = [species_obj1, species_obj2]
 	>>> result = phylotastic_services.update_list_data("abusalehmdtayeen@gmail.com", 57, species_list2,"ya29.Glt8BAvKKpEsU165zpbMEEoAGZOXh_qqSVln8Rsc_BTPLtQjURNUwbd7Dv6mzIvG6A6DJjgC3fyv9uIJ3wkH_9Rbu4W7zXvyNEu9Y-T2FrdXOiabiSEngGbBl19c")
	>>> print result
	{"user_id": "abusalehmdtayeen@gmail.com", "date_modified": "2017-07-03T20:08:02.532157", "status_code": 200, "old_species": [{"family": "Aceraceae", "scientific_name": "Acer ginnala", "scientific_name_authorship": "Maxim.", "order": "Sapindales", "vernacular_name": "Amur maple", "phylum": "Streptophyta", "nomenclature_code": "ICN", "class": ""}], "new_species": [{"family": "Aceraceae", "scientific_name": "Acer ginnala", "scientific_name_authorship": "Maxim.", "vernacular_name": "Amur maple", "phylum": "Streptophyta", "nomenclature_code": "ICN", "order": "Sapindales"}, {"family": "Amaranthaceae", "scientific_name": "Achyranthes japonica", "scientific_name_authorship": "(Miq.) Nakal", "vernacular_name": "Japanses chaff flower", "phylum": "Streptophyta", "nomenclature_code": "ICN", "order": "Caryophyllales"}], "list_id": 57, "list_title": "Illinois Invasive Plants", "message": "Success"}

	:param userId: Unique id (a valid gmail address) of a user. 
	:type userId: string.
	:param listId: Unique id of the list that needs to be modified. 
	:type listId: integer.
	:param speciesList: A list of species objects. 
	:type speciesList: A list of instances of the **Species** class
	:param accessToken: Access token for the user with userId (valid gmail address). 
	:type accessToken: string.  

	:returns: A json formatted string -- with new species object as a value of the ``new_species`` property. 
	"""
 	method = "/replace_species"
 	api_url = base_url + method
    
 	payload_data = {
 		'user_id': userId,
 		'list_id': listId,
 		'access_token': accessToken,
 		'species': speciesList
 	}
 	jsonPayload = json.dumps(payload_data, cls=ComplexEncoder)
 	
 	response = requests.post(api_url, data=jsonPayload, headers=headers)
 	
 	if response.status_code == requests.codes.ok:    
 		return response.text
 	else:
 		return json.dumps({"status_code": 500, "message": "Error connecting with species list server"})

#---------------------------------------------
def get_list_info(userId=None, listId=None, accessToken=None, verbose=None, content=None):
	"""Gets lists of species that exist in the species list server.

	Example:

	>>> import phylotastic_services
 	>>> result = phylotastic_services.get_list_info(userId="abusalehmdtayeen@gmail.com", listId=57, accessToken="ya29.Glt8BAvKKpEsU165zpbMEEoAGZOXh_qqSVln8Rsc_BTPLtQjURNUwbd7Dv6mzIvG6A6DJjgC3fyv9uIJ3wkH_9Rbu4W7zXvyNEu9Y-T2FrdXOiabiSEngGbBl19c")
	>>> print result
	{"list": {"list_title": "Illinois Invasive Plants", "list_species": ["Acer ginnala", "Achyranthes japonica"], "list_id": 57}, "message": "Success", "user_id": "abusalehmdtayeen@gmail.com", "status_code": 200}

	:param userId: Unique id (a valid gmail address) of a user. 
	:type userId: string.
	:param listId: Unique id of the list that needs to be retrieved. 
	:type listId: integer.
	:param accessToken: Access token for the user with userId (valid gmail address). 
	:type accessToken: string.
	:param verbose: By default *false* and allows to show minimal meta-data of the list. 
	:type verbose: boolean  
	:param content: By default *true* and allows to show the species collection of the list 
	:type content: boolean  

	:returns: A json formatted string -- with list object as a value of the ``list`` property. 
	"""	
 	method = "/get_list"
 	api_url = base_url + method
    
 	payload_data = {}
 	if userId is not None:
 		payload_data['user_id'] = userId
 	if listId is not None:
 		payload_data['list_id'] = listId
 	if accessToken is not None:
 		payload_data['access_token'] = accessToken,
 	if verbose is not None:	
 		payload_data['verbose']= verbose
 	if content is not None:	
 		payload_data['content']= content
 	
 	response = requests.get(api_url, params=payload_data) 

 	if response.status_code == requests.codes.ok:    
 		return response.text
 	else:
 		return json.dumps({"status_code": 500, "message": "Error connecting with species list server"})
	
#----------------------------------------------
def remove_list_info(userId, listId, accessToken):
	"""Removes an existing list from species list server.

	Example:

	>>> import phylotastic_services
 	>>> result = phylotastic_services.remove_list_info(userId="abusalehmdtayeen@gmail.com", listId=57, accessToken="ya29.Glt9BMHJWIYVeH2vHs_O4cGqtb8nWYdVu_dz4CNXVmRdIoX9-sd88MBLRAzmsH_JhhKB_qDTPppn3Iast6C8-g-ty3zKsri6sEm3_R6Lw3bHymCFDDgCHyQsthOH")
	>>> print result
	{"user_id": "abusalehmdtayeen@gmail.com", "status_code": 200, "list_id": 57, "date_removed": "2017-07-03T20:40:24.561842", "list_title": "Illinois Invasive Plants", "message": "Success"}

	:param userId: Unique id (a valid gmail address) of a user. 
	:type userId: string.
	:param listId: Unique id of the list that needs to be retrieved. 
	:type listId: integer.
	:param accessToken: Access token for the user with userId (valid gmail address). 
	:type accessToken: string.
	
	:returns: A json formatted string -- with title of the list removed as a value of the ``list_title`` property. 
	"""	
 	method = "/remove_list"
 	api_url = base_url + method
    
 	payload_data = {
 		'user_id': userId,
 		'list_id': listId,
 		'access_token': accessToken
 	}
 	
 	response = requests.get(api_url, params=payload_data) 

 	if response.status_code == requests.codes.ok:    
 		return response.text
 	else:
 		return json.dumps({"status_code": 500, "message": "Error connecting with species list server"})

#--------------------------------------------   

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#if __name__ == '__main__':

	#species_obj1 = Species("Acer ginnala", "Amur maple", "Maxim.", "Aceraceae","Sapindales", "Streptophyta", "ICN")
 	#species_obj2 = Species("Achyranthes japonica", "Japanses chaff flower", "(Miq.) Nakal", "Amaranthaceae", "Caryophyllales", "Streptophyta", "ICN")
 	#species_list1 = [species_obj1]
 	#species_list2 = [species_obj1, species_obj2]
 	#list_obj = List("Illinois Invasive Plants", "This list contains the invasive species, with their Family and Order", ["Invasive.org  Center for Invasive Species and Ecosystem Health"], "06-25-2017", "HD Laughinghouse", "2-25-2016", "http://www.invasive.org/species/list.cfm?id=152", ["Plants", " invasive species", " Illinois"], "Embryophyta", "", "script", True, species_list1)
 	
 	#print insert_list_info("abusalehmdtayeen@gmail.com", list_obj)

 	#list_obj = List(description="This list contains the invasive species", is_public=False)
 	#print update_list_metadata("abusalehmdtayeen@gmail.com", 57, list_obj, "ya29.Glt9BMHJWIYVeH2vHs_O4cGqtb8nWYdVu_dz4CNXVmRdIoX9-sd88MBLRAzmsH_JhhKB_qDTPppn3Iast6C8-g-ty3zKsri6sEm3_R6Lw3bHymCFDDgCHyQsthOH")
 	
 	#print update_list_data("abusalehmdtayeen@gmail.com", 57, species_list2, "ya29.Glt9BMHJWIYVeH2vHs_O4cGqtb8nWYdVu_dz4CNXVmRdIoX9-sd88MBLRAzmsH_JhhKB_qDTPppn3Iast6C8-g-ty3zKsri6sEm3_R6Lw3bHymCFDDgCHyQsthOH")
 	#print get_list_info(userId="abusalehmdtayeen@gmail.com", listId=57, accessToken="ya29.Glt9BMHJWIYVeH2vHs_O4cGqtb8nWYdVu_dz4CNXVmRdIoX9-sd88MBLRAzmsH_JhhKB_qDTPppn3Iast6C8-g-ty3zKsri6sEm3_R6Lw3bHymCFDDgCHyQsthOH")
 	#print get_list_info(userId="abusalehmdtayeen@gmail.com", content=False, accessToken="ya29.Glt8BP7TxEO5-ME5NiaO-bk0h-Mk06KCRLkwh7DIvsm6SZ_ReVArG_ySECvdVFagncyGA6u0CKLul53QsK6-Wo2ffNQITKdYGhOHLqjmjIDaXNIPHU84-aMFoPF7")
 	#print remove_list_info(userId="abusalehmdtayeen@gmail.com", listId=57, accessToken="ya29.Glt9BMHJWIYVeH2vHs_O4cGqtb8nWYdVu_dz4CNXVmRdIoX9-sd88MBLRAzmsH_JhhKB_qDTPppn3Iast6C8-g-ty3zKsri6sEm3_R6Lw3bHymCFDDgCHyQsthOH")
