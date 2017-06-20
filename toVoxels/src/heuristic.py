import pointcloud_proc
import numpy as np
import colorsys



"""
if a coordinate (i,j,k) is surrounded by 3 or more blocks, 
create a new block with the most common color between his neighbors

"""

def join(matrix):
    new_matrix = pointcloud_proc.SparseMatrix({}, matrix.resolution, matrix.bcube)
    
    neighbor = 0
    neighbor_colors = [0]*18
    
    
    
    resolution = matrix.resolution
    n=0;
    
    for i in range(0,resolution[0]):
        for j in range(0,resolution[1]):
            for k in range(0,resolution[2]):
                if (i,j,k) in matrix.values:
                    new_matrix.values[(i,j,k)] = (1,matrix.values[(i,j,k)][1])
                else:
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
                            
                        if(i-p,j-p,k) in matrix.values:
                            neighbor_colors[matrix.values[(i-p,j-p,k)][1]]+=1
                            neighbor+=1
                                 
                    if (neighbor > 3):
                        n+=1
                        new_matrix.values[(i,j,k)] = (1,neighbor_colors.index(max(neighbor_colors)))
                    neighbor_colors = [0]*18
                    neighbor = 0  
    print(n)
    return new_matrix




"""
Change the color tuple of each block depending on his neighbor
"""
def mergeColors(matrix):
    new_matrix = pointcloud_proc.SparseMatrix({}, matrix.resolution, matrix.bcube)
    neighbor_colors = [0]*18
    new_score = neighbor_colors
    
    resolution = matrix.resolution
    
    for i in range(0,resolution[0]):
        for j in range(0,resolution[1]):
            for k in range(0,resolution[2]):
                if (i,j,k) in matrix.values:
                    
                    #new_matrix.values[(i,j,k)] = (1,matrix.values[(i,j,k)][1])
                    for p in [-1, 1]:
                        if(i+p,j,k) in matrix.values:
                            neighbor_colors[matrix.values[(i+p,j,k)][1]]+=1
                        if(i,j+p,k) in matrix.values:
                            neighbor_colors[matrix.values[(i,j+p,k)][1]]+=1
                        if(i+p,j+p,k) in matrix.values:
                            neighbor_colors[matrix.values[(i+p,j+p,k)][1]]+=1
                            
                        if(i-p,j-p,k) in matrix.values:
                            neighbor_colors[matrix.values[(i-p,j-p,k)][1]]+=1
                            
                    
                    for n in range(0, 15):
                        new_score[n]=matrix.values[(i,j,k)][2][n]-neighbor_colors[n]*10
                    
                    
                    
                    min = new_score[0]
                    best = 0
                    for n in range(0, 15):
                        if (new_score[n] < min):
                            min = new_score[n]
                            best = n
            
                    if((best==13) | (best==5)):
                        new_matrix.values[(i,j,k)] = (1,16,new_score)
                    else:
                        new_matrix.values[(i,j,k)] = (1,best,new_score)
                                 
                    #print(new_matrix.values[(i,j,k)])
                    neighbor_colors = [0]*18
                    new_score = neighbor_colors
    return new_matrix

"""
For each block, create 3 more blocks with the same color

"""
def expandBlocks(matrix):
    new_matrix = pointcloud_proc.SparseMatrix({}, matrix.resolution, matrix.bcube)
    resolution = matrix.resolution
    for i in range(0,resolution[0]):
        for j in range(0,resolution[1]):
            for k in range(0,resolution[2]):
                if (i,j,k) in matrix.values:
                    new_matrix.values[(i,j,k)] = matrix.values[(i,j,k)]
                    if (i+1,j,k) not in matrix.values:
                        new_matrix.values[(i+1,j,k)] = matrix.values[(i,j,k)]
                    if (i,j+1,k) not in matrix.values:
                        new_matrix.values[(i,j+1,k)] = matrix.values[(i,j,k)]
                    if (i+1,j+1,k) not in matrix.values:
                        new_matrix.values[(i+1,j+1,k)] = matrix.values[(i,j,k)]
                        
    return new_matrix


"""
if a block does not have any block in his 26 block neighborhood, delete that block
"""
def deleteIsolated(matrix):
    resolution = matrix.resolution
    for i in range(0,resolution[0]):
        for j in range(0,resolution[1]):
            for k in range(0,resolution[2]):
                if (i,j,k) in matrix.values:
                    if pointcloud_proc.SparseMatrix.neighbor_26(matrix,(i,j,k)) == None:
                        del matrix.values[(i,j,k)]
                        
    return matrix



"""
If two blocks share the same i and j value, create a column between them.
"""
def createWalls(matrix):
    
    new_matrix = pointcloud_proc.SparseMatrix({}, matrix.resolution, matrix.bcube)
    populated = False
    h = 0
    neighbor = False
    
    resolution = matrix.resolution
    for i in range(0,resolution[0]):
        for j in range(0,resolution[1]):
            populated = False
            h = 0
            for k in range(resolution[2],0,-1):
                if populated:
                    
                    neighbor = ((i+1,j,k) in matrix.values) | ((i-1,j,k) in matrix.values) | ((i,j+1,k) in matrix.values) | ((i,j-1,k) in matrix.values)
                    
                    if neighbor:
                        for n in range(k,h):
                                new_matrix.values[(i,j,n)] = (1,8)
                        neighbor = False
                        h = k
                else:
                    if (i,j,k) in matrix.values:
                        populated = True
                        h = k
                        new_matrix.values[(i,j,k)] = matrix.values[(i,j,k)]
                    
                    
    return new_matrix
                
                        
def deleteTrees(matrix):
    num = 0
    resolution = matrix.resolution
    for i in range(0,resolution[0]):
        for j in range(0,resolution[1]):
            for k in range(0,resolution[2]):
                #print((i,j,k))
                if (i,j,k) in matrix.values:
                    if (matrix.values[(i,j,k)][1] == 16) & (k > 8):
                        ground = False
                        h=1
                        while (ground==False) & (h!=k):
                            h+=1
                            neighbor = 0
                            for p in [-1, 1]:
                                if(i+p,j,k-h) in matrix.values:
                                    neighbor+=1
                                if(i,j+p,k-h) in matrix.values:
                                    neighbor+=1
                                if(i+p,j+p,k-h) in matrix.values:
                                    neighbor+=1
                                if(i-p,j-p,k-h) in matrix.values:
                                    neighbor+=1
                                    
                            if ((neighbor > 2) & ((k-h)<9)):
                                ground = True
                                num+=1
                                if(num%30==0):
                                    matrix.values[(i,j,k-h+1)] = (1,17)
                                matrix.values[(i,j,k-h)] = (1,16)
                                del matrix.values[(i,j,k)]
                                
                        
    return matrix


"""
Change color brightness for a rgb tuple
"""
def changeBrightness(red,green,blue, n):
    rgb = np.vstack((red, green, blue)).transpose()
    hsv = [ colorsys.rgb_to_hsv(h[0]/65025., h[1]/65025., h[2]/65025.) for h in rgb]
    rgb = [ colorsys.hsv_to_rgb(h[0], h[1], h[2] + n) for h in hsv]
    red = [ int(h[0]*255) for h in rgb]
    green = [ int(h[1]*255) for h in rgb]
    blue = [ int(h[2]*255) for h in rgb]
    
    return (red, green, blue)
