
import numpy as np
from laspy.file import File


inFile = File("resources/PNOA_2010_LOTE1_ARA-NORTE_674-4618_ORT-CLA-COL.las", mode = "r")


#Se guardan las coordenadas de los puntos como tres listas diferentes (x, y, z) en la variable coords
coords = np.vstack((inFile.x, inFile.y, inFile.z))


print("Extrayendo la zona del EINA")
keep_points = coords[0] > 675500
keep_points2 = (4616500 < coords[1]) & ( coords[1] < 4617000)
keep_points3 = keep_points & keep_points2

# Grab an array of all points which meet this threshold
points_kept = inFile.points[keep_points3]

outFile1 = File("resources/EINA.las", mode = "w", header = inFile.header)
outFile1.points = points_kept
outFile1.close()
