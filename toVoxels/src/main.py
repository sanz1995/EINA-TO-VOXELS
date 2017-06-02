import numpy as np
from laspy.file import File
import pointcloud_proc



inFile = File("./resources/EINA.las", mode = "r")


colors = [(221,221,221),(219,125,62),(179,80,188),(107,138,201),(177,166,39),(65,174,56),(208,132,153),(64,64,64),(154,161,161),(46,110,137),(126,61,181),(46,56,141),(79,50,31),(53,70,27),(150,52,48),(25,22,22)]

print(colors)

#print(max(inFile.red))


#Se guardan las coordenadas en la variable coord como una unica lista de coordenadas (x, y, z)
coords = np.vstack((inFile.x, inFile.y, inFile.z, inFile.red, inFile.green, inFile.blue)).transpose()
print(coords)

#Numero de celdas para x, y, z
resolution = (250, 250, 45)

#Esquinas max y min de la estructura
bcube = {'min': (675500.0, 4616500.0, 192.37),'max': (676000.0, 4617000.0, 282.74)}


print("Creando matriz")
matrix = pointcloud_proc.SparseMatrix.create_from_coords(coords, resolution, bcube)


f = open('../../cubos.txt', 'w')


cells = matrix.values.keys()


for cell in cells:
    #if matrix.values[cell] > 1:
        #print(matrix.values[cell])
    f.write("%d %d %d %d\n" % (cell[0],cell[1],cell[2],matrix.values[cell][1]))
    
f.close()
print("Finalizado")




#print("Generando cluster a partir de la matriz")
#cluster = pointcloud_proc.cluster_matrix_from_cell_matrix(matrix)
#print("Exportando a fichero .js")
#pointcloud_proc.cells_to_Threejs(cluster[1], matrix, "/home/jorge/cosas/TFG/visor_threejs/data3d/pcloud.js", 1, 1, "box", None, True)


