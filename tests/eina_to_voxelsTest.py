import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import eina_to_voxels
import unittest

class TestEina_to_voxels(unittest.TestCase):
    
    def setUp(self):
        self.map = eina_to_voxels.Map()
        
        
    def testBasic(self):
        self.map.read("resources/EINA.las")
        self.map.writeMatrix("resources/out.txt")
    
    def testHeuristicWithoutOpenStreetMap(self):
        self.map.read("resources/EINA.las")
        self.map.useHeuristic()
        self.map.writeMatrix("resources/out.txt")
    
        
        
    def testOpenStreetMap(self):
        self.map.read("resources/EINA.las")
        self.map.useOpenStreetMap()
        self.map.writeMatrix("resources/out.txt")
        
        
    def testFull(self):
        self.map.read("resources/EINA.las")
        self.map.useOpenStreetMap()
        self.map.useHeuristic()
        self.map.writeMatrix("resources/out.txt")

    
    def testAddBuilding(self):
        self.map.read("resources/EINA.las")
        self.map.addBuilding("resources/adaByron.binvox",62,49,5)
        self.map.addSign(5,5)
        self.map.writeMatrix("resources/out.txt")
        
        
    
    def testAddBuildingWithHeuristic(self):
        self.map.read("resources/EINA.las")
        self.map.addBuilding("resources/adaByron.binvox",62,49,5)
        self.map.useHeuristic()
        self.map.createWalls()
        self.map.writeMatrix("resources/out.txt")
    


if __name__ == '__main__':
    unittest.main()