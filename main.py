
import numpy as np
from laspy.file import File
import pointcloud_proc
import heuristic
import binvox_rw
import openStreetMap
import sys

def writeMatrix(name, matrix):
    f = open(name, 'w')
    cells = matrix.values.keys()
    for cell in cells:
        f.write("%d %d %d %d\n" % (matrix.resolution[0]-cell[0],cell[1],cell[2],matrix.values[cell][1]))

    f.close()

def addBuilding(name,matrix, x, y, z, dirtyMatrix, xSign, ySign):
    
    with open(name, 'rb') as f:
        model = binvox_rw.read_as_3d_array(f)
    for i in range (0,model.dims[0]):
        for j in range (0,model.dims[1]):
            for k in range (0,model.dims[2]):
                dirtyMatrix[i+x][k+y] = False
                if model.data[i][k][j]:
                    matrix.values[(i+x,k+y,j+z)]= (1,8)
                    
    
    n = 0
    while (x,y,z+n) in matrix.values:
        n+=1
                    
    matrix.values[(xSign,ySign,z+n)]= (1,19)


if __name__ == '__main__':


    inFile = File(sys.argv[1], mode = "r")

    osm = openStreetMap.OpenStreetMap(sys.argv[2])
    
    # Colores sin modificar
    rgb = (inFile.Red/255, inFile.Green/255, inFile.Blue/255)
    
    
    # Modificar el brillo de los colores
    #rgb = heuristic.changeBrightness(inFile.Red,inFile.Green,inFile.Blue,0.05)
    
    
    #Se guardan las coordenadas en la variable coord como una unica lista de coordenadas (x, y, z)
    coords = np.vstack((inFile.x, inFile.y, inFile.z, rgb[0], rgb[1], rgb[2])).transpose()
    
    
    
    #Numero de celdas para x, y, z
    resolution = (500, 500, 90)
    
    #Esquinas max y min de la estructura
    bcube = {'min': (675500.0, 4616500.0, 192.37),'max': (676000.0, 4617000.0, 282.74)}
    
    
    print("Creando matriz")

    matrix = pointcloud_proc.SparseMatrix.create_from_coords(coords, resolution, bcube)
    
    
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
    
    addBuilding('../resources/adaByron.binvox',matrix,162,249,5,dirtyMatrix,226,263)
    
    matrix = heuristic.createWalls(matrix,dirtyMatrix,green)
    
    
    writeMatrix(sys.argv[3], matrix)
    
    print("Finalizado")
    

