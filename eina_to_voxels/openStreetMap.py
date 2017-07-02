from osgeo import ogr
import utm
import osmapi
import pointcloud_proc

class OpenStreetMap:
    
    
    def readMap(self, name):
        
        api = osmapi.OsmApi()
        file = open(name, "r")
        
        self.area = api.ParseOsm(file.read())
        
        self.dict = {}
        
        self.green = ogr.Geometry(ogr.wkbMultiPolygon)
        self.roads = ogr.Geometry(ogr.wkbMultiLineString)
    
    
        for item in self.area:
            self.dict[item.get("data").get("id")] = item.get("data")
            
        file.close()
        
    def downloadMap(self, minX, minY, maxX, maxY):
        api = osmapi.OsmApi()
        #file = open(name, "r")
        
        minUTM = utm.to_latlon(minX, minY, 30, 'U')
        
        maxUTM = utm.to_latlon(maxX, maxY, 30, 'U')
        
        self.area = api.Map(minUTM[1], minUTM[0], maxUTM[1], maxUTM[0])
        
        self.dict = {}
        
        self.green = ogr.Geometry(ogr.wkbMultiPolygon)
        self.roads = ogr.Geometry(ogr.wkbMultiLineString)
    
    
        for item in self.area:
            self.dict[item.get("data").get("id")] = item.get("data")
            
        #file.close()
        

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
    Given an SparseMatrix, it returns a list of pairs (x, y) from the matrix, 
    where every pair of the list is a green zone. It also returns a list of pairs for roads.
    
    """
    
    def intersectWithMatrix(self,matrix):
        greenBlocks = []
        roadBlocks = []
        
        self.getGreenZone()
        self.getRoads()
        
        resolution = matrix.resolution
        for i in range (0,resolution[0]):
            for j in range(0,resolution[1]):
                point = ogr.Geometry(ogr.wkbPoint)
                
                coord = pointcloud_proc.cell_to_coords((i,j,0),resolution,matrix.bcube)
                point.AddPoint(coord[0],coord[1])
                if point.Intersects(self.green):
                    greenBlocks.append((i,j))
                    
                if point.Intersects(self.green):
                    greenBlocks.append((i,j))
                if point.Distance(self.roads) < 3:
                    roadBlocks.append((i,j))
        return (greenBlocks, roadBlocks)



def addNodesToMultiPol(dict, nodes, multiPol):
    ring = ogr.Geometry(ogr.wkbLinearRing)
    
    for node in nodes:
        utmCoords = utm.from_latlon(dict[node].get("lat"),dict[node].get("lon"))
        ring.AddPoint(utmCoords[0],utmCoords[1])
     
    utmCoords = utm.from_latlon(dict[nodes[0]].get("lat"),dict[nodes[0]].get("lon"))
    ring.AddPoint(utmCoords[0],utmCoords[1])
    
    
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    
    if poly.IsValid():
        multiPol.AddGeometry(poly)
        
            
     
    
def addNodesToLine(dict, nodes, multiLine):  
    line = ogr.Geometry(ogr.wkbLineString)
    for node in nodes:
        utmCoords = utm.from_latlon(dict[node].get("lat"),dict[node].get("lon"))
        line.AddPoint(utmCoords[0],utmCoords[1])
        
    multiLine.AddGeometry(line)
    
    