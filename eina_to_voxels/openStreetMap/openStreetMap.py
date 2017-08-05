from osgeo import ogr
import utm
import osmapi
import matplotlib.pyplot as plt 
import json
import time
import math
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pointcloud_proc

class OpenStreetMap:
    
    """
    src is the path of an openStreetMap file. The program reads the map and creates
     a dictionaty with its values  
    """
    def readMap(self, src):
        
        api = osmapi.OsmApi()
        file = open(src, "r")
        
        self.area = api.ParseOsm(file.read())
        
        self.dict = {}
        
        self.green = ogr.Geometry(ogr.wkbMultiPolygon)
        self.roads = ogr.Geometry(ogr.wkbMultiLineString)
    
    
        for item in self.area:
            self.dict[item.get("data").get("id")] = item.get("data")
            
        file.close()
       
       
    """
    The program downloads an openStreetMap file for the coordinates given and creates
     a dictionaty with its values  
    """ 
    def downloadMap(self, minX, minY, maxX, maxY):
        api = osmapi.OsmApi()
        #file = open(name, "r")
        
        minUTM = utm.to_latlon(minX, minY, 30, 'U')
        
        maxUTM = utm.to_latlon(maxX, maxY, 30, 'U')
        
        self.area = api.Map(minUTM[1], minUTM[0], maxUTM[1], maxUTM[0])
        
        self.dict = {}
        
        self.green = ogr.Geometry(ogr.wkbMultiPolygon)
        self.buildings = ogr.Geometry(ogr.wkbMultiPolygon)
        self.roads = ogr.Geometry(ogr.wkbMultiLineString)
    
    
        for item in self.area:
            self.dict[item.get("data").get("id")] = item.get("data")
            
        

    """
    Returns a Multipolygon containing each area of grass, park or vegetation
    """
    
    def getGreenZone(self):
        
        if self.green.IsEmpty():
            for item in self.area:
                if item.get("type")=="way":
                    data = item.get("data")
                    tag = data.get("tag")
                    if (tag.get("landuse") == "grass") | (tag.get("leisure") == "park") | (tag.get("natural") == "wood"):
                        addNodesToMultiPol(self.dict, data.get("nd"), self.green)
                elif item.get("type")=="relation":
                    data = item.get("data")
                    tag = data.get("tag")
                    if (tag.get("landuse") == "grass") | (tag.get("leisure") == "park") | (tag.get("natural") == "wood"):
                        nodes = []
                        for way in data.get("member"):
                            if way.get("ref") in self.dict:
                                nodes += self.dict[way.get("ref")].get("nd")
                        addNodesToMultiPol(self.dict, nodes, self.green)
                        
        return self.green
    
    
    
    """
    Returns a Multipolygon containing each area of building
    """
    
    def getBuildings(self):
        
        if self.buildings.IsEmpty():
            for item in self.area:
                if item.get("type")=="way":
                    data = item.get("data")
                    tag = data.get("tag")
                    if (tag.get("building") != "") & (tag.get("building") != None):
                        addNodesToMultiPol(self.dict, data.get("nd"), self.buildings)
                
                elif item.get("type")=="relation":
                    data = item.get("data")
                    tag = data.get("tag")
                    if (tag.get("building") != "") & (tag.get("building") != None):
                        nodes = []
                        for way in data.get("member"):
                            if way.get("ref") in self.dict:
                                if self.dict[way.get("ref")].get("nd") != None:
                                    nodes += self.dict[way.get("ref")].get("nd")
                        addNodesToMultiPol(self.dict, nodes, self.buildings)
                        
        return self.buildings



    """
    Returns a multiline containing each road in the area whose type is residential, secondary or service.
    """
    def getRoads(self):
        if self.roads.IsEmpty():
            for item in self.area:
                if item.get("type")=="way":
                    data = item.get("data")
                    tag = data.get("tag")
                    if (tag.get("highway") == "residential") | (tag.get("highway") == "secondary") | (tag.get("highway") == "service"):
                        addNodesToLine(self.dict, data.get("nd"), self.roads)
            
                    
        return self.roads
    
    """
    Given an SparseMatrix, another matrix with True value for every coordinate located in a green zone, 
    It also returns a matrix for roads and buildings.
    
    """
    
    def intersectWithMatrix(self,matrix):
        self.getGreenZone()
        self.getBuildings()
        self.getRoads()
        
        
        
        
        resolution = matrix.resolution
        
        
        greenBlocks = [[True for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
        roadBlocks = [[True for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
        buildingBlocks = [[True for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
        
        
        
        for i in range (0,resolution[0]):
            for j in range(0,resolution[1]):
                point = ogr.Geometry(ogr.wkbPoint)
                coord = pointcloud_proc.cell_to_coords((i,j,0),resolution,matrix.bcube)
                point.AddPoint(coord[0],coord[1])
                
                
                if greenBlocks[i][j]:
                    distance = int(point.Distance(self.green))
                    
                    #if distance > 0:
                        #greenBlocks[i][j] = False
                        
                    for p in range (-distance, distance):
                        for q in range (-distance, distance):
                            #print (i+p,j+q)
                            if ((i+p >= 0) & (i+p < resolution[0])) & ((j+q >= 0) & (j+q < resolution[1])) & (math.sqrt(math.pow(p,2) + math.pow(q,2)) < distance):
                                greenBlocks[i+p][j+q] = False
                                
                if roadBlocks[i][j]:    
                    distance = int(point.Distance(self.roads))    
                    
                    for p in range (-distance, distance):
                        for q in range (-distance, distance):
                            #print (i+p,j+q)
                            if ((i+p >= 0) & (i+p < resolution[0])) & ((j+q >= 0) & (j+q < resolution[1])) & (math.sqrt(math.pow(p,2) + math.pow(q,2)) < distance - 2):
                                #print (i+p,j+q)
                                roadBlocks[i+p][j+q] = False
                                
                if buildingBlocks[i][j]:                     
                    distance = int(point.Distance(self.buildings))  
                                
                    for p in range (-distance, distance):
                        for q in range (-distance, distance):
                            #print (i+p,j+q)
                            if ((i+p >= 0) & (i+p < resolution[0])) & ((j+q >= 0) & (j+q < resolution[1])) & (math.sqrt(math.pow(p,2) + math.pow(q,2)) < distance - 5):
                                #print (i+p,j+q)
                                buildingBlocks[i+p][j+q] = False
                
                """
                #24 seg
                if point.Distance(self.green) == 0:
                    greenBlocks[i][j] = True
                #32 seg
                if point.Distance(self.roads) < 3:
                    roadBlocks[i][j] = True
                #24 seg
                if point.Distance(self.buildings) < 6:
                    buildingBlocks[i][j] = True
                    
                """
                
        return (greenBlocks, roadBlocks, buildingBlocks)


def addNodesToMultiPol(dict, nodes, multiPol):
    ring = ogr.Geometry(ogr.wkbLinearRing)
    
    for node in nodes:
        utmCoords = utm.from_latlon(dict[node].get("lat"),dict[node].get("lon"))
        ring.AddPoint(utmCoords[0],utmCoords[1])
     
    utmCoords = utm.from_latlon(dict[nodes[0]].get("lat"),dict[nodes[0]].get("lon"))
    ring.AddPoint(utmCoords[0],utmCoords[1])
    
    
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    #plot(poly.Simplify(1))
    #print "simplify"
    
    if poly.IsValid():
        multiPol.AddGeometry(poly)
        
            
     
    
def addNodesToLine(dict, nodes, multiLine):  
    line = ogr.Geometry(ogr.wkbLineString)
    for node in nodes:
        utmCoords = utm.from_latlon(dict[node].get("lat"),dict[node].get("lon"))
        line.AddPoint(utmCoords[0],utmCoords[1])
        
    multiLine.AddGeometry(line)
    
    
def plot(geometry):
    
    ax = plt.figure().gca()
    coords = json.loads(geometry.ExportToJson())['coordinates']
    x = [i for i,j,k in coords[0]]
    y = [j for i,j,k in coords[0]]
    ax.plot(x,y)
    ax.axis('scaled')
    plt.show()
    
    