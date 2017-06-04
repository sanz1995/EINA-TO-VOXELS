import numpy as np
from laspy.file import File
import pointcloud_proc



inFile = File("./resources/EINA.las", mode = "r")


#colors = [(221,221,221,1),(219,125,62,1.2),(179,80,188,1.2),(107,138,201,1,1),(177,166,39,1),(65,174,56,1),(208,132,153,1.1),(64,64,64,1),(154,161,161,1),(46,110,137,1),(126,61,181,1.1),(46,56,141,1),(79,50,31,1),(53,70,27,1),(150,52,48,1.1),(25,22,22,1)]

#print(colors)

#print(max(inFile.red))


#Se guardan las coordenadas en la variable coord como una unica lista de coordenadas (x, y, z)
coords = np.vstack((inFile.x, inFile.y, inFile.z, inFile.red, inFile.green, inFile.blue)).transpose()
#print(inFile)
#13056

#Numero de celdas para x, y, z
resolution = (500, 500, 90)

#Esquinas max y min de la estructura
bcube = {'min': (675500.0, 4616500.0, 192.37),'max': (676000.0, 4617000.0, 282.74)}


print("Creando matriz")
matrix = pointcloud_proc.SparseMatrix.create_from_coords(coords, resolution, bcube)


f = open('../../cubos.txt', 'w')


       
pointcloud_proc.deleteIsolated(matrix)




for i in range(0,2):
    matrix = pointcloud_proc.join(matrix)

cells = matrix.values.keys()



for cell in cells:
    #if matrix.values[cell] > 1:
        #print(matrix.values[cell])
 #   print(pointcloud_proc.SparseMatrix.neighbor_6(matrix,cell))
  #  print(cell)
   # print("----------")
    f.write("%d %d %d %d\n" % (resolution[0]-cell[0],cell[1],cell[2],matrix.values[cell][1]))
    
f.close()
print("Finalizado")





#print("Generando cluster a partir de la matriz")
#cluster = pointcloud_proc.cluster_matrix_from_cell_matrix(matrix)
#print("Exportando a fichero .js")
#pointcloud_proc.cells_to_Threejs(cluster[1], matrix, "/home/jorge/cosas/TFG/visor_threejs/data3d/pcloud.js", 1, 1, "box", None, True)


