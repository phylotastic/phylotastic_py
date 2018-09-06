from unittest import TestCase
import json
import phylotastic_services

class TestGetTraits(TestCase):
    def test_get_traits_EOL(self):
        """
        Testing getting habitat and conservation status of a list of species from EOL traitsbank
        """
        result = phylotastic_services.get_traits_EOL(["Balaenoptera musculus"])
        # Check whether result is what it should be according to docs
        self.assertTrue(u'oceanic zone' in json.loads(result)['species'][0]['habitats'])
        self.assertTrue(u'endangered' in json.loads(result)['species'][0]['conservation_status'])
        

    def test_get_traits_ECOS(self):
        """
        Testing getting conservation status of a list of species using ECOS services
        """
        result = phylotastic_services.get_traits_ECOS(["Loxodonta africana"])
        # Check whether result is what it should be according to docs
        self.assertTrue(u'Threatened' in json.loads(result)['species'][0]['conservation_status'])
        
    
