import heuristic

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pointcloud_proc

class MergeColors(heuristic.Heuristic):
    
    def __init__(self, param):
        super(MergeColors,self).__init__(param)
        
    """
    Change the color tuple of each block depending on his neighbor
    """
    def apply(self, world):
        
        matrix = world.matrix
        
        new_matrix = pointcloud_proc.SparseMatrix({}, matrix.resolution, matrix.bcube)
        neighbor_colors = [0]*30
        new_score = neighbor_colors
        
        resolution = matrix.resolution
        
        for i in range(0,resolution[0]):
            for j in range(0,resolution[1]):
                for k in range(0,resolution[2]):
                    if (i,j,k) in matrix.values:
                        
                        #new_matrix.values[(i,j,k)] = (1,matrix.values[(i,j,k)][1])
                        for p in (0, 1):
                            if(i+p,j,k) in matrix.values:
                                neighbor_colors[matrix.values[(i+p,j,k)][1]]+=1
                            if(i-p,j,k) in matrix.values:
                                neighbor_colors[matrix.values[(i-p,j,k)][1]]+=1
                            if(i,j+p,k) in matrix.values:
                                neighbor_colors[matrix.values[(i,j+p,k)][1]]+=1
                            if(i,j-p,k) in matrix.values:
                                neighbor_colors[matrix.values[(i,j-p,k)][1]]+=1
                            if(i+p,j+p,k) in matrix.values:
                                neighbor_colors[matrix.values[(i+p,j+p,k)][1]]+=1
                            if(i-p,j-p,k) in matrix.values:
                                neighbor_colors[matrix.values[(i-p,j-p,k)][1]]+=1
                                
                        
                        for n in range(0, 16):
                            new_score[n]=matrix.values[(i,j,k)][2][n]-neighbor_colors[n]*30
                        
                        min = new_score[0]
                        best = 0
                        for n in range(0, 16):
                            if (new_score[n] < min):
                                min = new_score[n]
                                best = n
                
                        if((best==13) | (best==5)):
                            new_matrix.values[(i,j,k)] = (1,16,new_score)
                        else:
                            new_matrix.values[(i,j,k)] = (1,best,new_score)
                                     
                        #print(new_matrix.values[(i,j,k)])
                        neighbor_colors = [0]*20
                        new_score = neighbor_colors
                        
                        
        world.matrix = new_matrix
        return world