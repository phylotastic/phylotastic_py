from unittest import TestCase
import json
import phylotastic_services

class TestGetTree(TestCase):
    def test_get_tree_OpenTree(self):
        """
        Testing getting a phylogenetic tree from a list of taxa using Open Tree of Life APIs
        """
        result = phylotastic_services.get_tree_OpenTree(taxa=["Setophaga striata","Setophaga magnolia","Setophaga angelae","Setophaga plumbea","Setophaga virens"])

        self.assertTrue(u'newick' in result)
        #self.assertTrue(u'newick' in result)
        self.assertTrue(u'Setophaga_magnolia_ott532751' in result[u'newick'])
        self.assertTrue(u'tree_metadata' in result)
        result_metadata = result[u'tree_metadata']
        self.assertTrue(u'supporting_studies' in result_metadata)
        self.assertTrue(len(result_metadata[u'supporting_studies']) >= 2)

    #-------------------------------------
    def test_get_tree_Phylomatic(self):
        """
        Testing getting a phylogenetic tree from a list of taxa using Phylomatic API
        """
        result = phylotastic_services.get_tree_Phylomatic(taxa=["Annona cherimola", "Annona muricata", "Quercus robur", "Shorea parvifolia"])
        
        self.assertTrue('newick' in result)
        self.assertTrue('Annona_muricata' in result[u'newick'])
        self.assertTrue('Quercus_robur' in result[u'newick'])
        
    #--------------------------------------
    '''
    def test_get_tree_NCBI(self):
        """
        Testing getting a phylogenetic tree from a list of taxa based on NCBI taxonomy using PhyloT
        """
        result = phylotastic_services.get_tree_NCBI(taxa=["Panthera uncia", "Panthera onca", "Panthera leo", "Panthera pardus"])

        self.assertTrue(u'newick' in result)
        self.assertTrue(u'Panthera_pardus' in result[u'newick'])
        self.assertTrue(u'Panthera_uncia' in result[u'newick'])
    '''    
        

