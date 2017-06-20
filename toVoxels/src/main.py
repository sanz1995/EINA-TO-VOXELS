import numpy as np
from laspy.file import File
import pointcloud_proc
import heuristic
import binvox_rw


def writeMatrix(f,matrix,resolution):
    cells = matrix.values.keys()
    for cell in cells:
        f.write("%d %d %d %d\n" % (resolution[0]-cell[0],cell[1],cell[2],matrix.values[cell][1]))

def addBuilding(name,matrix, x, y, z):
    with open(name, 'rb') as f:
        model = binvox_rw.read_as_3d_array(f)
    for i in range (0,model.dims[0]):
        for j in range (0,model.dims[1]):
            for k in range (0,model.dims[2]):
                if model.data[i][k][j]:
                    matrix.values[(i+x,k+y,j+z)]= (1,8)
    


def main():
    
    inFile = File("./resources/EINA.las", mode = "r")
    
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
    
    
    f = open('../../cubos.txt', 'w')
    
           
    
    matrix=heuristic.deleteIsolated(matrix)
    
       
    matrix=heuristic.mergeColors(matrix)
    
    
    matrix=heuristic.expandBlocks(matrix)
    
    
    for i in range (0, 1):
        matrix=heuristic.deleteTrees(matrix)
    
    
    for i in range (0, 1):
        matrix=heuristic.join(matrix)
    
    
    #matrix = heuristic.createWalls(matrix)

    addBuilding('./resources/adaByron.binvox',matrix,161,249,5)
    
    writeMatrix(f, matrix, resolution)
    
    f.close()
    print("Finalizado")


main()






#print("Generando cluster a partir de la matriz")
#cluster = pointcloud_proc.cluster_matrix_from_cell_matrix(matrix)
#print("Exportando a fichero .js")
#pointcloud_proc.cells_to_Threejs(cluster[1], matrix, "/home/jorge/cosas/TFG/visor_threejs/data3d/pcloud.js", 1, 1, "box", None, True)


