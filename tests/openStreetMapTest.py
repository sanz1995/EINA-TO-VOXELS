import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import eina_to_voxels

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../eina_to_voxels')))

import openStreetMap
import unittest

class TestOpenStreetMap(unittest.TestCase):
    
    def setUp(self):
        self.osm = openStreetMap.OpenStreetMap()
        
        
    def testBasic(self):
        self.osm.downloadMap(675000,4617100,675200,4617300)
        
        self.assertEqual(0,self.osm.getGreenZone().GetPointCount())
        self.assertEqual(0,self.osm.getRoads().GetPointCount())
        
    
    def testGetAreas(self):
        self.osm.downloadMap(675000,4617100,675200,4617300)
        green = self.osm.getGreenZone()
        roads = self.osm.getRoads()
        
        self.osm.downloadMap(675000,4617100,675200,4617300)
        
        self.assertEqual(green.GetPointCount(),self.osm.getGreenZone().GetPointCount())
        self.assertEqual(roads.GetPointCount(),self.osm.getRoads().GetPointCount())
    
    
    
    def testIntersectWithMatrix(self):
        
        map = eina_to_voxels.Map()
        map.read("resources/EINA.las")
        
        matrix = map.matrix
        
        min = matrix.bcube.get("min")
        max = matrix.bcube.get("max")
        
        self.osm.downloadMap(min[0],min[1],max[0],max[1])
         
        self.osm.intersectWithMatrix(matrix)
        
    

if __name__ == '__main__':
    unittest.main()