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
        
        
        num = 5
        resolution = matrix.resolution
        x, y, z = resolution
        cluster = [[[[] for i in range(z/num + (z%num > 0))] for j in range(y/num + (y%num > 0))] for k in range(x/num + (x%num > 0))]
        
        cells = matrix.values.keys()
        for (i,j,k) in cells:
            cluster[int(i/num)][int(j/num)][int(k/num)].append((i,j,k))
            
            
        for p in range(0,resolution[0]/num):
            for q in range(0,resolution[1]/num):
                for r in range(0,resolution[2]/num):
                    for myCell in cluster[p][q][r]:
                        #new_matrix.values[myCell] = matrix.values[myCell]
                        
                        for otherCell in cluster[p][q][r]:
                            if myCell != otherCell:
                                neighbor_colors[matrix.values[otherCell][1]]+=1
                        
                        for n in range(0, 16):
                            new_score[n]=matrix.values[myCell][2][n]-neighbor_colors[n]*30
                        
                        min = new_score[0]
                        best = 0
                        for n in range(0, 16):
                            if (new_score[n] < min):
                                min = new_score[n]
                                best = n
                        #print myCell
                        if((best==13) | (best==5)):
                            new_matrix.values[myCell] = (1,16,new_score)
                        else:
                            new_matrix.values[myCell] = (1,best,new_score)
                                     
                        neighbor_colors = [0]*30
                        new_score = neighbor_colors
                        
                            
        #for c in new_matrix.values.keys():
        #    print new_matrix.values[c]
        world.matrix = new_matrix
        print world
        return world
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
        
        """