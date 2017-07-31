import heuristic

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pointcloud_proc

class ExpandBlocks(heuristic.Heuristic):
    
    def __init__(self, param):
        super(ExpandBlocks,self).__init__(param)
        
    """
    For each block, create 3 more blocks with the same color
    """
    def apply(self, world):
        
        
        matrix = world.matrix
        
        new_matrix = pointcloud_proc.SparseMatrix({}, matrix.resolution, matrix.bcube)
        #resolution = matrix.resolution
        cells = matrix.values.keys()
        for (i,j,k) in cells:
            new_matrix.values[(i,j,k)] = matrix.values[(i,j,k)]
            if (i+1,j,k) not in matrix.values:
                new_matrix.values[(i+1,j,k)] = matrix.values[(i,j,k)]
            if (i,j+1,k) not in matrix.values:
                new_matrix.values[(i,j+1,k)] = matrix.values[(i,j,k)]
            if (i+1,j+1,k) not in matrix.values:
                new_matrix.values[(i+1,j+1,k)] = matrix.values[(i,j,k)]
                    
        world.matrix = new_matrix        
        return world