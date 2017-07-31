import heuristic
import copy

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pointcloud_proc

class Join(heuristic.Heuristic):
    
    def __init__(self, param):
        super(Join,self).__init__(param)
        
    """

    if a coordinate (i,y,k) with k < z is surrounded by 3 or more blocks, 
    create a new block with the most common color between his neighbors. 
    The program alse creates some trees if for blocks created in a green zone
    
    """
    def apply(self, world):
        
        matrix = world.matrix
        green = world.green
        
        new_matrix = pointcloud_proc.SparseMatrix(copy.copy(matrix.values), matrix.resolution, matrix.bcube)
        neighbor = 0
        neighbor_colors = [0]*20
        num = 0
        
        z = self.param[0]
        
        resolution = matrix.resolution
        
        for i in range(0,resolution[0]):
            for j in range(0,resolution[1]):
                for k in range(0,z):
                    if (i,j,k) not in matrix.values:
                        for p in [-1, 1]:
                            if(i+p,j,k) in matrix.values:
                                neighbor_colors[matrix.values[(i+p,j,k)][1]]+=1
                                neighbor+=1
                            if(i,j+p,k) in matrix.values:
                                neighbor_colors[matrix.values[(i,j+p,k)][1]]+=1
                                neighbor+=1
                            if(i+p,j+p,k) in matrix.values:
                                neighbor_colors[matrix.values[(i+p,j+p,k)][1]]+=1
                                neighbor+=1
                                
                            if(i+p,j-p,k) in matrix.values:
                                neighbor_colors[matrix.values[(i+p,j-p,k)][1]]+=1
                                neighbor+=1
                                
                        if (neighbor > 3):
                            #print neighbor
                            #print neighbor_colors
                            color = neighbor_colors.index(max(neighbor_colors))
                            
                            new_matrix.values[(i,j,k)] = (1,color)
                            if (color == 16) & (green[i][j]):
                                num+=1
                                if num%30 == 0:
                                    createTree(new_matrix,world,i,j,k)
                        neighbor_colors = [0]*20
                        neighbor = 0
                        
        world.matrix = new_matrix
        return world
    
    
"""
Create a tree in the coordinates given
"""
def createTree(matrix,world,x,y,z):
    
    green = world.green
    buildings = world.buildings
    
    space = True
    if green[x][y] & (buildings[x][y] == False) & \
        green[x+1][y] & (buildings[x+1][y] == False) & \
        green[x-1][y] & (buildings[x-1][y] == False) & \
        green[x][y+1] & (buildings[x][y+1] == False) & \
        green[x][y-1] & (buildings[x][y-1] == False) & \
        green[x+1][y+1] & (buildings[x+1][y+1] == False) & \
        green[x+1][y-1] & (buildings[x+1][y-1] == False) & \
        green[x-1][y-1] & (buildings[x-1][y-1] == False) & \
        green[x-1][y+1] & (buildings[x-1][y+1] == False):
        space = True
    else:
        space = False
        
        
    for i in range(1,matrix.resolution[2]):
        for j in range(1,5):
            if ((x,y,z+i) in matrix.values) | \
                ((x+j,y,z+i) in matrix.values) | \
                ((x-j,y,z+i) in matrix.values) | \
                ((x,y+j,z+i) in matrix.values) | \
                ((x,y-j,z+i) in matrix.values) | \
                ((x+j,y+j,z+i) in matrix.values) | \
                ((x+j,y-j,z+i) in matrix.values) | \
                ((x-j,y+j,z+i) in matrix.values) | \
                ((x-j,y-j,z+i) in matrix.values):
                space = False
                
    if space:
        matrix.values[(x,y,z+1)] = (1,17)
        matrix.values[(x,y,z+2)] = (1,17)
        matrix.values[(x,y,z+3)] = (1,17)
        matrix.values[(x,y,z+4)] = (1,17)
        for i in range(5,10):
            matrix.values[(x,y,z+i)] = (1,17)
            matrix.values[(x+1,y,z+i)] = (1,18)
            matrix.values[(x-1,y,z+i)] = (1,18)
            matrix.values[(x,y+1,z+i)] = (1,18)
            matrix.values[(x,y-1,z+i)] = (1,18)
            matrix.values[(x+1,y+1,z+i)] = (1,18)
            matrix.values[(x-1,y-1,z+i)] = (1,18)
            matrix.values[(x+1,y-1,z+i)] = (1,18)
            matrix.values[(x-1,y+1,z+i)] = (1,18)
        matrix.values[(x,y,z+10)] = (1,18)
