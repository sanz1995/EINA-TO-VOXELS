import numpy as np
from laspy.file import File
import pointcloud_proc
import heuristic
import openStreetMap
import binvox_rw


class Map:
    
    def __init__(self):
        
        self.osm = openStreetMap.OpenStreetMap()
        
        
    
    def read(self, src):
        
        inFile = File(src, mode = "r")
        
        # Colores sin modificar
        rgb = (inFile.Red/255, inFile.Green/255, inFile.Blue/255)
        
        
        # Modificar el brillo de los colores
        #rgb = heuristic.changeBrightness(inFile.Red,inFile.Green,inFile.Blue,0.05)
        
        
        #Se guardan las coordenadas en la variable coord como una unica lista de coordenadas (x, y, z)
        coords = np.vstack((inFile.x, inFile.y, inFile.z, rgb[0], rgb[1], rgb[2])).transpose()
        
        self.xMin = min(inFile.x)
        self.yMin = min(inFile.y)
        self.zMin = min(inFile.z)
        
        self.xMax = max(inFile.x)
        self.yMax = max(inFile.y)
        self.zMax = max(inFile.z)
        
        
        
        #Numero de celdas para x, y, z
        resolution = (int(round(self.xMax - self.xMin)), int(round(self.yMax - self.yMin)), int(round(self.zMax - self.zMin)))
    
        #Esquinas max y min de la estructura
        bcube = {'min': (self.xMin, self.yMin, self.zMin),'max': (self.xMax, self.yMax, self.zMax)}
        
        
        #print("Creando matriz")
    
        self.matrix = pointcloud_proc.SparseMatrix.create_from_coords(coords, resolution, bcube)
        
        
        self.dirtyMatrix = [[True for j in range(resolution[0])] for k in range(resolution[1])]
        
        self.green = [[False for j in range(resolution[0])] for k in range(resolution[1])]
        
        self.roads = [[False for j in range(resolution[0])] for k in range(resolution[1])]
    
    
    def useOpenStreetMap(self):
        self.osm.downloadMap(self.xMin,self.yMin,self.xMax,self.yMax)
        
        list = self.osm.intersectWithMatrix(self.matrix)
    
        self.green = list[0]
        self.roads = list[1]
        
        self.matrix=heuristic.setRoads(self.matrix,self.roads)
        self.matrix=heuristic.setGreenZone(self.matrix,self.green)
    
    
    
    def useOpenStreetMapFromFile(self, src):
        self.osm.readMap(src)
        
        list = self.osm.intersectWithMatrix(self.matrix)
    
        self.green = list[0]
        self.roads = list[1]
        
        self.matrix=heuristic.setRoads(self.matrix,self.roads)
        self.matrix=heuristic.setGreenZone(self.matrix,self.green)
        
        
    def useHeuristic(self):
        
        self.matrix=heuristic.deleteIsolated(self.matrix)
        
        self.matrix=heuristic.expandBlocks(self.matrix)
    
        for i in range (0, 5):
            self.matrix=heuristic.deleteTrees(self.matrix,self.green)
            
        
        for i in range (0, 0):
            self.matrix=heuristic.join(self.matrix)
            
            
        for i in range (0, 0):
            self.matrix=heuristic.join2(self.matrix,7)
            
    
    
    def addBuilding(self,src, x, y, z):
        with open(src, 'rb') as f:
            model = binvox_rw.read_as_3d_array(f)
        for i in range (0,model.dims[0]):
            for j in range (0,model.dims[1]):
                for k in range (0,model.dims[2]):
                    self.dirtyMatrix[i+x][k+y] = False
                    if model.data[i][k][j]:
                        self.matrix.values[(i+x,k+y,j+z)]= (1,8)
                        
        
        
    def addSign(self, x, y):
        n = 0
        while (x,y,n) in self.matrix.values:
            n+=1
            
        self.matrix.values[(x,y,n)]= (1,19)
        
        
    
    def createWalls(self):
        matrix = heuristic.createWalls(self.matrix,self.dirtyMatrix,self.green)
        
        
    
    def writeMatrix(self,dest):
        f = open(dest, 'w')
        cells = self.matrix.values.keys()
        for cell in cells:
            f.write("%d %d %d %d\n" % (self.matrix.resolution[0]-cell[0],cell[1],cell[2],self.matrix.values[cell][1]))
    
        f.close()
        
        
        