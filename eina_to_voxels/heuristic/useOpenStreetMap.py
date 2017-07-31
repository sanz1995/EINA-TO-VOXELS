import heuristic

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pointcloud_proc
import openStreetMap

class UseOpenStreetMap(heuristic.Heuristic):
    
    def __init__(self, param):
        super(UseOpenStreetMap,self).__init__(param)
        
    """
    For each block, create 3 more blocks with the same color
    """
    def apply(self, world):
        
        matrix = world.matrix
        
        world.openStreetMap = True
        
        osm = openStreetMap.OpenStreetMap()
        
        
        xMin = matrix.bcube.get("min")[0]
        yMin = matrix.bcube.get("min")[1]
        
        xMax = matrix.bcube.get("max")[0]
        yMax = matrix.bcube.get("max")[1]
        
        
        osm.downloadMap(xMin,yMin,xMax,yMax)
        
        #self.osm.getBuildings()
        
        list = osm.intersectWithMatrix(matrix)
    
        world.green = list[0]
        world.roads = list[1]
        world.buildings = list[2]
        
        
        setRoads(matrix,world.roads)
        setGreenZone(matrix,world.green)
        
           
        return world
    
    
"""
Change color to green in every block located in a green zone
"""
def setGreenZone(matrix,green):
    for i in range(matrix.resolution[0]):
        for j in range(matrix.resolution[1]):
            if green[i][j]:
                for k in range(matrix.resolution[2]):
                    if (i,j,k) in matrix.values:
                        matrix.values[(i,j,k)] = (1,16)
            


"""
Change the color to dark gray in every block located in a road
"""
def setRoads(matrix,roads):
    for i in range(matrix.resolution[0]):
        for j in range(matrix.resolution[1]):
            if roads[i][j]:
                for k in range(matrix.resolution[2]):
                    if (i,j,k) in matrix.values:
                        matrix.values[(i,j,k)] = (1,7)