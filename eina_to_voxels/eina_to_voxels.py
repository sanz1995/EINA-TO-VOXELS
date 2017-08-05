import numpy as np
from laspy.file import File
import pointcloud_proc
import openStreetMap
import colorsys
import worldDTO
import time


class World:
    
    def __init__(self, src):
        
        self.osm = openStreetMap.OpenStreetMap()
        self.heuristics = []
        
        
        inFile = File(src, mode = "r")
        
        xMin = min(inFile.x)
        yMin = min(inFile.y)
        zMin = min(inFile.z)
        
        xMax = max(inFile.x)
        yMax = max(inFile.y)
        zMax = max(inFile.z)
        
        if ((xMax - xMin) <= 1000):
            
            # Colores sin modificar
            #rgb = (inFile.Red/255, inFile.Green/255, inFile.Blue/255)
            
            # Modificar el brillo de los colores
            rgb = changeBrightness(inFile.Red,inFile.Green,inFile.Blue)
            
            #Se guardan las coordenadas en la variable coord como una unica lista de coordenadas (x, y, z)
            coords = np.vstack((inFile.x, inFile.y, inFile.z, rgb[0],rgb[1],rgb[2])).transpose()
            
            
            #Numero de celdas para x, y, z
            resolution = (int(round(xMax - xMin)), int(round(yMax - yMin)), int(round(zMax - zMin)))
        
            #Esquinas max y min de la estructura
            bcube = {'min': (xMin, yMin, zMin),'max': (xMax, yMax, zMax)}
            
            
            print("Creando matriz")
        
            self.matrix = pointcloud_proc.SparseMatrix.create_from_coords(coords, resolution, bcube)
            
            self.myBuildings = [[False for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
            
            self.green = [[False for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
            
            self.roads = [[False for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
        
            self.buildings = [[False for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
            
            
            self.openStreetMap = False
        else:
            print "El fichero es demasiado grande, puedes partirlo con la funcion splitFile()"
            
        
        
        
    def add(self, heuristic):
        self.heuristics.append(heuristic)   
        
        
    def start(self):
        w = worldDTO.WorldDTO(self.matrix, self.roads, self.green, self.buildings, self.myBuildings, self.openStreetMap)
        print "|||||||"
        print self.matrix.resolution[0]
        print "|||||||"
        for h in self.heuristics:
            start = time.time()
            w = h.apply(w) 
            print h
            print time.time()-start
            print "-----------"
            
        self.matrix = w.matrix
        self.roads = w.roads
        self.green = w.green
        self.buildings = w.buildings
        self.myBuildings = w.myBuildings
        self.openStreetMap = w.openStreetMap
            
    """
    dest is the path of the file where the program exports the world 
    """
    def exportWorld(self,dest):
        f = open(dest, 'w')
        cells = self.matrix.values.keys()
        for cell in cells:
            if self.matrix.values[cell][1] == 19:
                f.write("%d %d %d %d %s\n" % (self.matrix.resolution[0]-cell[0],cell[1],cell[2],self.matrix.values[cell][1],self.matrix.values[cell][2]))
            else:
                f.write("%d %d %d %d\n" % (self.matrix.resolution[0]-cell[0],cell[1],cell[2],self.matrix.values[cell][1]))
    
        f.close()
        
        
"""
Change color brightness for a rgb tuple
"""
def changeBrightness(red,green,blue):
    rgb = np.vstack((red, green, blue)).transpose()
    hsv = [ colorsys.rgb_to_hsv(h[0]/65025., h[1]/65025., h[2]/65025.) for h in rgb]
    """
    print hsv[0][2]
    print hsv[1][2]
    print hsv[2][2]
    print "--------"
    print h[2] + 0.2*(1-h[2])
    print (0.2 - (0.2*hsv[1][2])**2)
    print (0.2 - (0.2*hsv[2][2])**2)
    """
    #rgb = [ colorsys.hsv_to_rgb(h[0], h[1], 0.5) for h in hsv]
    rgb = [ colorsys.hsv_to_rgb(h[0], h[1], h[2] + 0.2*((1-h[2])**2)) for h in hsv]
    #rgb = [ colorsys.hsv_to_rgb(h[0], h[1], h[2] + (1 ** h[2])/10) for h in hsv]
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
        
    
            
    
            