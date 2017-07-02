
import numpy as np
from laspy.file import File
import pointcloud_proc
import heuristic
import openStreetMap
import sys

if __name__ == '__main__':


    inFile = File(sys.argv[1], mode = "r")
    
    
    # Colores sin modificar
    rgb = (inFile.Red/255, inFile.Green/255, inFile.Blue/255)
    
    
    # Modificar el brillo de los colores
    #rgb = heuristic.changeBrightness(inFile.Red,inFile.Green,inFile.Blue,0.05)
    
    
    #Se guardan las coordenadas en la variable coord como una unica lista de coordenadas (x, y, z)
    coords = np.vstack((inFile.x, inFile.y, inFile.z, rgb[0], rgb[1], rgb[2])).transpose()
    
    
    
    #Numero de celdas para x, y, z
    resolution = (int(round(max(inFile.x) - min(inFile.x))), int(round(max(inFile.y) - min(inFile.y))), int(round(max(inFile.z) - min(inFile.z))))

    #Esquinas max y min de la estructura
    bcube = {'min': (min(inFile.x), min(inFile.y), min(inFile.z)),'max': (max(inFile.x), max(inFile.y), max(inFile.z))}
    
    
    print("Creando matriz")

    matrix = pointcloud_proc.SparseMatrix.create_from_coords(coords, resolution, bcube)
    
    
    
    osm = openStreetMap.OpenStreetMap()
    
    if len(sys.argv) > 4:
        osm.readMap(sys.argv[4])
    else:
        osm.downloadMap(min(inFile.x),min(inFile.y),max(inFile.x),max(inFile.y))
        
    list = osm.intersectWithMatrix(matrix)
    
    green = list[0]
    roads = list[1]
    
    matrix=heuristic.setRoads(matrix,roads)
    matrix=heuristic.setGreenZone(matrix,green)
    
    
    matrix=heuristic.expandBlocks(matrix)
    
    
    for i in range (0, 5):
        matrix=heuristic.deleteTrees(matrix,green)
        
    
    for i in range (0, 0):
        matrix=heuristic.join(matrix)
        
        
    for i in range (0, 0):
        matrix=heuristic.join2(matrix,7)
    
    

    dirtyMatrix = [[True for j in range(resolution[0])] for k in range(resolution[1])]
    
    if len(sys.argv) > 3:
        heuristic.addBuilding(sys.argv[3],matrix,162,249,5,dirtyMatrix,226,263)
    
    matrix = heuristic.createWalls(matrix,dirtyMatrix,green)
    
    
    pointcloud_proc.writeMatrix(sys.argv[2], matrix)
    
    print("Finalizado")
    

