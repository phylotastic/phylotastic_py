from unittest import TestCase
import json
import phylotastic_services

class TestExtractNames(TestCase):
    def test_extract_names_GNRD_URL(self):
        """
        Testing extract names from URL using GNRD
        """
        result = phylotastic_services.extract_names_URL("https://en.wikipedia.org/wiki/Plain_pigeon")
        # Check whether the number of names in the result is more than the minimum expected
        self.assertTrue(len(json.loads(result)[u'scientificNames']) > 5)
        # Check whether result is what it should be according to docs
        self.assertTrue(u'Patagioenas inornata' in json.loads(result)[u'scientificNames'])


    def test_extract_names_TaxonFinder_URL(self):
        """
        Testing extract names from URL using TaxonFinder
        """
        result = phylotastic_services.extract_names_URL("https://en.wikipedia.org/wiki/Cave_Bear", "taxonfinder")
        # Check whether the number of names in the result is more than the minimum expected
        self.assertTrue(len(json.loads(result)[u'scientificNames']) > 10)
        # Check whether result is what it should be according to docs
        self.assertTrue(u'Ursus spelaeus' in json.loads(result)[u'scientificNames'])
        self.assertTrue(u'Ursus etruscus' in json.loads(result)[u'scientificNames'])
        self.assertTrue(u'Ursus arctos' in json.loads(result)[u'scientificNames'])
 

    def test_extract_names_GNRD_TEXT(self):
        """
        Testing extract names from TEXT using GNRD 
        """
        result = phylotastic_services.extract_names_TEXT("The lemon dove (Columba larvata) is a species of bird in the pigeon family Columbidae found in montane forests of sub-Saharan Africa.", "gnrd")
        # Check whether the number of names in the result is more than the minimum expected
        self.assertTrue(len(json.loads(result)[u'scientificNames']) >= 2)
        # Check whether result is what it should be according to docs
        self.assertTrue(u'Columba larvata' in json.loads(result)[u'scientificNames'])


    def test_extract_names_TaxonFinder_TEXT(self):
        """
        Testing extract names from TEXT using TaxonFinder
        """
        result = phylotastic_services.extract_names_TEXT("Formica polyctena is a species of European red wood ant in the genus Formica.", "taxonfinder")
        # Check whether the number of names in the result is more than the minimum expected
        self.assertTrue(len(json.loads(result)[u'scientificNames']) >= 1)
        # Check whether result is what it should be according to docs
        self.assertTrue(u'Formica polyctena' in json.loads(result)[u'scientificNames'])
