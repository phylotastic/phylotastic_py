from unittest import TestCase
import json
import phylotastic_services

class TestGetInfo(TestCase):
    def test_get_eolurls_species(self):
        """
        Testing get information urls of a list of species from EOL
        """
        result = phylotastic_services.get_eolurls_species(["Panthera leo", "Panthera onca"])
        self.assertTrue(json.loads(result)[u'species'] >= 2)
        # Check whether result is what it should be according to docs
        result_list = json.loads(result)[u'species']
        for result in result_list: 
            if result['searched_name'] == "Panthera leo":
               self.assertTrue(u'https://eol.org/pages/328672' in result['species_info_link'])
            elif result['searched_name'] == "Panthera onca":
               self.assertTrue(u'https://eol.org/pages/328606' in result['species_info_link'])
        

    def test_get_images_species(self):
        """
        Testing gets image urls and corresponding license information of a list of species from EOL
        """
        result = phylotastic_services.get_images_species(["Rangifer tarandus"])
        # Check whether the number of names in the result is more than the minimum expected
        self.assertTrue(json.loads(result)[u'species'] >= 1)
        image_list = json.loads(result)[u'species'][0]['images']
        # Check whether result is what it should be according to docs
        for image in image_list:
           if "http://media.eol.org/content/2014/05/02/09/88803_orig.jpg" in image['eolMediaURL']:       
               self.assertTrue(True) 

    
