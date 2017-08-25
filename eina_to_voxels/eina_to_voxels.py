import numpy as np
from laspy.file import File
import pointcloud_proc
import openStreetMap
import colorsys
import worldDTO
import resource

def using(point=""):
    usage=resource.getrusage(resource.RUSAGE_SELF)
    return '''%s: usertime=%s systime=%s mem=%s mb
           '''%(point,usage[0],usage[1],
                (usage[2]*resource.getpagesize())/1000000.0 )


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


        
        
    def add(self, heuristic):
        self.heuristics.append(heuristic)   
        
        
    def start(self):
        w = worldDTO.WorldDTO(self.matrix)
        
        for h in self.heuristics:
            w = h.apply(w) 
            print using("mem")
        self.matrix = w.matrix
                
    """
    dest is the path of the file where the program exports the world 
    """
    def exportWorld(self,dest):
        f = open(dest, 'w')
        
        
        resolution = self.matrix.resolution
        for x in range (0,resolution[0],30):
            for y in range (0,resolution[1],30):
                for z in range (0,resolution[2],30):
                    for i in range(0,30):
                        for j in range(0,30):
                            for k in range(0,30):
                                #print (x+i,y+j,z+k)
                                if (x+i,y+j,z+k) in self.matrix.values:
                                    cell = (x+i,y+j,z+k)
                                    #print cell
                                    f.write("%d %d %d %d\n" % (resolution[0]-cell[0],cell[1],cell[2],self.matrix.values[cell][1]))
                       
        
        f.close()
        
        
"""
Change color brightness for a rgb tuple
"""
def changeBrightness(red,green,blue):
    rgb = np.vstack((red, green, blue)).transpose()
    hsv = [ colorsys.rgb_to_hsv(h[0]/65025., h[1]/65025., h[2]/65025.) for h in rgb]
    
    rgb = [ colorsys.hsv_to_rgb(h[0], h[1], h[2] + 0.2*((1-h[2])**2)) for h in hsv]
    
    red = [ int(h[0]*255) for h in rgb]
    green = [ int(h[1]*255) for h in rgb]
    blue = [ int(h[2]*255) for h in rgb]
    
    return (red, green, blue)

