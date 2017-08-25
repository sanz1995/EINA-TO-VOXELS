import heuristic

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pointcloud_proc
import binvox_rw

class AddBuilding(heuristic.Heuristic):
    
    def __init__(self, param):
        super(AddBuilding,self).__init__(param)
        
    """
    if a block does not have any block in his 26 block neighborhood, delete that block
    """
    def apply(self,world):
        
        src = self.param[0]
        x = self.param[1]
        y = self.param[2]
        z = self.param[3]
        
        matrix = world.matrix
        myBuildings = world.myBuildings
        
        cell = pointcloud_proc.coords_to_cell((x,y,z), matrix.resolution, matrix.bcube)
        x = int(cell[0])
        y = int(cell[1])
        z = int(cell[2])
        
        with open(src, 'rb') as f:
            model = binvox_rw.read_as_3d_array(f)
            
        
        for i in range (0,model.dims[0]):
            for j in range (0,model.dims[1]):
                for k in range (0,model.dims[2]):
                    if model.data[i][k][j]:
                        myBuildings[i+x][k+y] = True
            
        for i in range (0,model.dims[0]):
            for j in range (0,model.dims[1]):
                for k in range (0,model.dims[2]):
                    if myBuildings[i+x][k+y]:
                        if (i+x,k+y,j+z) in matrix.values:
                            del matrix.values[(i+x,k+y,j+z)]
                    
                        if model.data[i][k][j]:
                            matrix.values[(i+x,k+y,j+z)]= (1,8)
                            #Update resolution
                            if (x + i) > matrix.resolution[0]:
                                matrix.resolution = ((x + i),matrix.resolution[1],matrix.resolution[2])
                            if (k + y) > matrix.resolution[1]:
                                matrix.resolution = (matrix.resolution[0],(k + y),matrix.resolution[2])
                            if (j + z) > matrix.resolution[2]:
                                matrix.resolution = (matrix.resolution[0],matrix.resolution[1],(j + z))
        return world