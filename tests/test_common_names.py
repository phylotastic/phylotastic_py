from unittest import TestCase
import json
import phylotastic_services

class TestCommonNames(TestCase):
    def test_get_scientific_names_ex1(self):
        """
        Testing Example 1 (NCBI): Getting scientific names of a list of species from their common names (vernacular names)
        """
        result = phylotastic_services.get_scientific_names(["american crow", "rock dove", "american robin", "barn owl", "bald eagle"])
        result_list = json.loads(result)['result']
        for result in result_list: 
            if result['searched_name'] == "rock dove":
               self.assertTrue(u'Columba livia' in result['matched_names'][0]['scientific_name'])
            elif result['searched_name'] == "american robin":
               self.assertTrue(u'Turdus migratorius' in result['matched_names'][0]['scientific_name'])
            elif result['searched_name'] == "bald eagle":
               self.assertTrue(u'Haliaeetus leucocephalus' in result['matched_names'][0]['scientific_name'])


    def test_get_scientific_names_ex2(self):
        """
        Testing Example 2 (ITIS): Getting scientific names of a list of species from their common names (vernacular names)
        """
        result = phylotastic_services.get_scientific_names(["domestic cattle","blue whale"], source="ITIS")
        result_list = json.loads(result)['result']
        for result in result_list: 
            if result['searched_name'] == "domestic cattle":
               self.assertTrue(u'Bos taurus' in result['matched_names'][0]['scientific_name'])
            elif result['searched_name'] == "blue whale":
               self.assertTrue(u'Balaenoptera musculus' in result['matched_names'][0]['scientific_name'])
            


    def test_get_scientific_names_ex3(self):
        """
        Testing Example 3 (TROPICOS): Getting scientific names of a list of species from their common names (vernacular names)
        """
        result = phylotastic_services.get_scientific_names(["ginger", "garlic"], source="TROPICOS")
        result_list = json.loads(result)['result']
        for result in result_list: 
            if result['searched_name'] == "ginger":
               self.assertTrue(u'Zingiber officinale' in result['matched_names'][0]['scientific_name'])
            elif result['searched_name'] == "garlic":
               self.assertTrue(u'Allium sativum' in result['matched_names'][0]['scientific_name'])
    
