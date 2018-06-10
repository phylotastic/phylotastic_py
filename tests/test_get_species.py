from unittest import TestCase
import json
import phylotastic_services

class TestGetSpecies(TestCase):
    def test_get_all_species(self):
        """
        Testing get all Species that belong to a particular Taxon
        """
        result = phylotastic_services.get_all_species("Vulpes")
        self.assertTrue(json.loads(result)[u'species'] >= 3)
        # Check whether result is what it should be according to docs
        self.assertTrue(u'Vulpes minimus' in json.loads(result)[u'species'])
        # Check whether result is what it should be according to docs
        self.assertTrue(u'Vulpes cascadensis' in json.loads(result)[u'species'])


    def test_get_country_species(self):
        """
        Testing get all species that belong to a particular taxon and established in a particular country
        """
        result = phylotastic_services.get_country_species("Vulpes", "Nepal")
        # Check whether the number of names in the result is more than the minimum expected
        self.assertTrue(json.loads(result)[u'species'] >= 2)
        
        # Check whether result is what it should be according to docs
        self.assertTrue(u'Vulpes bengalensis' in json.loads(result)[u'species'])
        # Check whether result is what it should be according to docs
        self.assertTrue(u'Vulpes ferrilata' in json.loads(result)[u'species'])

    def test_get_genome_species(self):
        """
        Testing get all species that belong to a particular taxon and have genome sequence in NCBI
        """
        result = phylotastic_services.get_genome_species("Felidae")
        # Check whether the number of names in the result is more than the minimum expected
        self.assertTrue(json.loads(result)[u'total_names'] >= 5)
        # Check whether result is what it should be according to docs
        self.assertTrue(u'Acinonyx jubatus' in json.loads(result)[u'species'])
        # Check whether result is what it should be according to docs
        self.assertTrue(u'Panthera pardus' in json.loads(result)[u'species'])
        # Check whether result is what it should be according to docs
        self.assertTrue(u'Felis catus' in json.loads(result)[u'species'])


