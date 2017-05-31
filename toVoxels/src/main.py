import numpy as np
from laspy.file import File
import pointcloud_proc


inFile = File("resources/EINA.las", mode = "r")


#Se guardan las coordenadas en la variable coord como una unica lista de coordenadas (x, y, z)
coords = np.vstack((inFile.x, inFile.y, inFile.z)).transpose()

#Numero de celdas para x, y, z
resolution = (1000, 1000, 45)

#Esquinas max y min de la estructura
bcube = {'min': (674000, 4616000, 192.37),'max': (676000, 4618000, 282.74)}


print("Creando matriz")
matrix = pointcloud_proc.SparseMatrix.create_from_coords(coords, resolution, bcube)


f = open('../../cubos.txt', 'w')

cells = matrix.values.keys()


for cell in cells:
    f.write("%d %d %d 0\n" % (cell[0],cell[1],cell[2]))
    
f.close()
print("Finalizado")




#print("Generando cluster a partir de la matriz")
#cluster = pointcloud_proc.cluster_matrix_from_cell_matrix(matrix)
#print("Exportando a fichero .js")
#pointcloud_proc.cells_to_Threejs(cluster[1], matrix, "/home/jorge/cosas/TFG/visor_threejs/data3d/pcloud.js", 1, 1, "box", None, True)


