import numpy as np
from laspy.file import File
import pointcloud_proc
import heuristic
import openStreetMap
import binvox_rw
import colorsys
import time

class World:
    
    
    
    def __init__(self):
        
        self.osm = openStreetMap.OpenStreetMap()
        
        
    """
    src is the path of a .las file. 
    The program reads the file and converts it to a sparse matrix. It also changes
    the colors given to avoid shadows and soften colors
    """
    def read(self, src):
        
        inFile = File(src, mode = "r")
        
        self.xMin = min(inFile.x)
        self.yMin = min(inFile.y)
        self.zMin = min(inFile.z)
        
        self.xMax = max(inFile.x)
        self.yMax = max(inFile.y)
        self.zMax = max(inFile.z)
        
        if ((self.xMax - self.xMin) <= 500):
            
            
            # Colores sin modificar
            #rgb = (inFile.Red/255, inFile.Green/255, inFile.Blue/255)
            
            # Modificar el brillo de los colores
            rgb = changeBrightness(inFile.Red,inFile.Green,inFile.Blue)
            
            
            #Se guardan las coordenadas en la variable coord como una unica lista de coordenadas (x, y, z)
            coords = np.vstack((inFile.x, inFile.y, inFile.z, rgb[0], rgb[1], rgb[2])).transpose()
            
            
            #Numero de celdas para x, y, z
            resolution = (int(round(self.xMax - self.xMin)), int(round(self.yMax - self.yMin)), int(round(self.zMax - self.zMin)))
        
            #Esquinas max y min de la estructura
            bcube = {'min': (self.xMin, self.yMin, self.zMin),'max': (self.xMax, self.yMax, self.zMax)}
            
            
            print("Creando matriz")
        
            self.matrix = pointcloud_proc.SparseMatrix.create_from_coords(coords, resolution, bcube)
            
            for i in range(0,3):
                self.matrix=heuristic.mergeColors(self.matrix)
            
            
            
            self.myBuildings = [[False for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
            
            self.green = [[False for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
            
            self.roads = [[False for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
        
            self.buildings = [[False for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
            
            
            self.openStreetMap = False
        else:
            print "El fichero es demasiado grande, puedes partirlo con la funcion splitFile()"
        
        
    """
    It downloads an openStreetMap with the previous size, gets information about green zones, 
    roads and building and changes the world to fit that information.
    """
    def useOpenStreetMap(self):
        self.openStreetMap = True
        
        self.osm.downloadMap(self.xMin,self.yMin,self.xMax,self.yMax)
        
        #self.osm.getBuildings()
        
        
        list = self.osm.intersectWithMatrix(self.matrix)
    
        self.green = list[0]
        self.roads = list[1]
        self.buildings = list[2]
        
        
        heuristic.setRoads(self.matrix,self.roads)
        heuristic.setGreenZone(self.matrix,self.green)
    
        
    
    """
    src is the path of an openStreetMap. The program gets information about green zones, 
    roads and building from the map and changes the world to fit that information.
    """
    def useOpenStreetMapFromFile(self, src):
        
        self.openStreetMap = True
        
        self.osm.readMap(src)
        
        list = self.osm.intersectWithMatrix(self.matrix)
    
        self.green = list[0]
        self.roads = list[1]
        self.buildings = list[2]
        
        heuristic.setRoads(self.matrix,self.roads)
        heuristic.setGreenZone(self.matrix,self.green)
        
    
    
    """
    The program uses some heuristics to improve general aspect
    
    """
    
    def useHeuristic(self):
        
        self.matrix=heuristic.deleteIsolated(self.matrix)

        for i in range (0,5):
            self.matrix=heuristic.deleteIsolatedGroups(self.matrix,self.buildings)
        
        
        self.matrix=heuristic.expandBlocks(self.matrix)
    
        
        for i in range (0, 10):
            self.matrix=heuristic.join(self.matrix,7,self.green)
            
        for i in range (0, 0):
            self.matrix=heuristic.join(self.matrix,self.matrix.resolution[2],self.green)
    
    
    """
    src is the path of a binvox file. The program reads the structure in the 
    binvox file and inserts it in the [x,y,z] coordinates of the world 
    
    """
    def addBuilding(self,src, x, y, z):
        with open(src, 'rb') as f:
            model = binvox_rw.read_as_3d_array(f)
        for i in range (0,model.dims[0]):
            for j in range (0,model.dims[1]):
                for k in range (0,model.dims[2]):
                    self.myBuildings[i+x][k+y] = True
                    if model.data[i][k][j]:
                        self.matrix.values[(i+x,k+y,j+z)]= (1,8)
                        #Update resolution
                        if (x + i) > self.matrix.resolution[0]:
                            self.matrix.resolution = ((x + i),self.matrix.resolution[1],self.matrix.resolution[2])
                        if (k + y) > self.matrix.resolution[1]:
                            self.matrix.resolution = (self.matrix.resolution[0],(k + y),self.matrix.resolution[2])
                        if (j + z) > self.matrix.resolution[2]:
                            self.matrix.resolution = (self.matrix.resolution[0],self.matrix.resolution[1],(j + z))
                        
                        
        
    
    """
    The program inserts a sign in the [x,y] coordinates of the world 
    """    
    def addSign(self, x, y):
        n = 0
        while (x,y,n) in self.matrix.values:
            n+=1
        self.matrix.values[(x,y,n)]= (1,19)
        
        
    """
    If openStreetMap was used before, the program use building information to create walls for that area.
    If openStreetMap was not used before, the program create walls for the whole world. 
    If some building was inserted before from a binvox file, the program does not create walls in that area. 
    
    """
    def createWalls(self):
        if self.openStreetMap == False:
            self.buildings = [[True for j in range(self.matrix.resolution[0]+1)] for k in range(self.matrix.resolution[1]+1)]
    
        heuristic.createWalls(self.matrix,self.myBuildings,self.buildings)
        
        
    
    """
    dest is the path of the file where the program exports the world 
    """
    def exportWorld(self,dest):
        f = open(dest, 'w')
        cells = self.matrix.values.keys()
        for cell in cells:
            f.write("%d %d %d %d\n" % (self.matrix.resolution[0]-cell[0],cell[1],cell[2],self.matrix.values[cell][1]))
    
        f.close()
    
    
"""
Change color brightness for a rgb tuple
"""
def changeBrightness(red,green,blue):
    rgb = np.vstack((red, green, blue)).transpose()
    hsv = [ colorsys.rgb_to_hsv(h[0]/65025., h[1]/65025., h[2]/65025.) for h in rgb]
    rgb = [ colorsys.hsv_to_rgb(h[0], h[1], h[2] + (1 ** h[2])/10) for h in hsv]
    red = [ int(h[0]*255) for h in rgb]
    green = [ int(h[1]*255) for h in rgb]
    blue = [ int(h[2]*255) for h in rgb]
    
    return (red, green, blue)



"""
src is the path of a .las file. Create a new .las file between (x1,y1) 
and (x2, y2) in UTM and store it in dest.
"""

def splitFile(src, dest, x1, y1, x2, y2):
    
    
    inFile = File(src, mode = "r")

    #Se guardan las coordenadas de los puntos como tres listas diferentes (x, y, z) en la variable coords
    coords = np.vstack((inFile.x, inFile.y, inFile.z))
    
    
    print("Extrayendo la zona seleccionada")
    
    keep_points = (coords[0] > x1) & (coords[0] < x2)
    keep_points2 = (y1 < coords[1]) & ( coords[1] < y2)
    keep_points3 = keep_points & keep_points2
    
    # Grab an array of all points which meet this threshold
    points_kept = inFile.points[keep_points3]
    
    outFile1 = File(dest, mode = "w", header = inFile.header)
    outFile1.points = points_kept
    outFile1.close()
        