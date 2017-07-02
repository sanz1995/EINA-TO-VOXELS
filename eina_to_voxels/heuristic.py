import pointcloud_proc
import numpy as np
import colorsys
import copy
import binvox_rw

"""
if a coordinate (i,y,k) is surrounded by 3 or more blocks, 
create a new block with the most common color between his neighbors

"""

def join(matrix):
    
    new_matrix = pointcloud_proc.SparseMatrix({}, matrix.resolution, matrix.bcube)
    
    neighbor = 0
    neighbor_colors = [0]*19
    
    
    
    resolution = matrix.resolution
    
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
                        new_matrix.values[(i,j,k)] = (1,neighbor_colors.index(max(neighbor_colors)))
                    neighbor_colors = [0]*19
                    neighbor = 0  
    return new_matrix





def join2(matrix, z):
    new_matrix = pointcloud_proc.SparseMatrix(copy.copy(matrix.values), matrix.resolution, matrix.bcube)
    neighbor = 0
    neighbor_colors = [0]*19
    
    
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
                            
                        if(i-p,j-p,k) in matrix.values:
                            neighbor_colors[matrix.values[(i-p,j-p,k)][1]]+=1
                            neighbor+=1
                                 
                    if (neighbor > 3):
                        new_matrix.values[(i,j,k)] = (1,neighbor_colors.index(max(neighbor_colors)))
                    neighbor_colors = [0]*19
                    neighbor = 0  
    return new_matrix




"""
Change the color tuple of each block depending on his neighbor
"""
def mergeColors(matrix):
    new_matrix = pointcloud_proc.SparseMatrix({}, matrix.resolution, matrix.bcube)
    neighbor_colors = [0]*19
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
                    neighbor_colors = [0]*19
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


def deleteIsolated2(matrix):
    n = 4
    
    resolution = matrix.resolution
    
    x, y, z = resolution;
    cluster = [[[[] for i in range(z/n + (z%n > 0))] for j in range(y/n + (y%n > 0))] for k in range(x/n + (x%n > 0))]
    #print (cluster)
    cells = matrix.values.keys()
    for (i,j,k) in cells:
        #print (i,j,k)
        cluster[int(i/n)][int(j/n)][int(k/n)].append((i,j,k))
    
    
    
    num = 0
    neighborhood = []
    value = 0
    for p in range(0,resolution[0]/n):
        for q in range(0,resolution[1]/n):
            for r in range(0,resolution[2]/n):
                if len(cluster[p][q][r]) > 0:
                    if ((p == 0) | (p == resolution[0]/n-1) | (q == 0) | (q == resolution[1]/n-1) | (r == 0) | (r == resolution[2]/n-1)):
                        neighborhood = cluster[p][q][r]
                    else:
                        neighborhood = cluster[p][q][r] + cluster[p+1][q][r] + cluster[p-1][q][r] + cluster[p][q+1][r] + cluster[p][q-1][r]
                    value = 0
                    for (i,j,k) in cluster[p][q][r]:
                        for h in range (1,6):
                            if (i+h,j,k) in neighborhood:
                                value += 1
                            if (i-h,j,k) in neighborhood:
                                value += 1
                            if (i,j+h,k) in neighborhood:
                                value += 1
                            if (i,j-h,k) in neighborhood:
                                value += 1
                        
                        
                    if (value/len(cluster[p][q][r]))<2:
                        num +=1
                        for (i,j,k) in cluster[p][q][r]:
                            del matrix.values[(i,j,k)]
                        
                    
    
                        
    return matrix



"""
If two blocks share the same i and j value, create a column between them.
"""
def createWalls(matrix, dirtyMatrix, green):
    
    #new_matrix = pointcloud_proc.SparseMatrix({}, matrix.resolution, matrix.bcube)
    populated = False
    h = 0
    neighbor = False
    
    resolution = matrix.resolution
    for i in range(0,resolution[0]):
        for j in range(0,resolution[1]):
            populated = False
            h = 0
            if dirtyMatrix[i][j]:
                for k in range(resolution[2],0,-1):
                    if populated:
                        
                        neighbor = ((i+1,j,k) in matrix.values) | ((i-1,j,k) in matrix.values) | ((i,j+1,k) in matrix.values) | ((i,j-1,k) in matrix.values)
                        
                        if neighbor:
                            for n in range(k,h):
                                if (i,j,n) not in matrix.values:
                                    matrix.values[(i,j,n)] = (1,8)
                            neighbor = False
                            h = k
                    else:
                        if (i,j,k) in matrix.values:
                            populated = True
                            h = k
                            #new_matrix.values[(i,j,k)] = matrix.values[(i,j,k)]
                """else:
                    if (i,j,k) in matrix.values:
                        new_matrix.values[(i,j,k)] = matrix.values[(i,j,k)]"""
                    
                    
    return matrix
                
                        
def deleteTrees(matrix,green):
    num = 0
    resolution = matrix.resolution
    for (i,j) in green:
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
                                createTree(matrix,i,j,k-h)
                            matrix.values[(i,j,k-h)] = (1,16)
                            del matrix.values[(i,j,k)]
                                
                        
    return matrix

def deleteTrees2(matrix):
    num = 0
    resolution = matrix.resolution
    for i in range(0,resolution[0]):
        for j in range(0,resolution[1]):
            for k in range(0,resolution[2]):
                #print((i,j,k))
                if (i,j,k) in matrix.values:
                    if (matrix.values[(i,j,k)][1] == 16) & (k > 8):
                        del matrix.values[(i,j,k)]
                                
                        
    return matrix

def createTree(matrix,x,y,z):
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
        


def setGreenZone(matrix,green):
    for (i,j) in green:
        for k in range(matrix.resolution[2]):
            if (i,j,k) in matrix.values:
                matrix.values[(i,j,k)] = (1,16)
    return matrix   
            


def setRoads(matrix,roads):
    for (i,j) in roads:
        for k in range(matrix.resolution[2]):
            if (i,j,k) in matrix.values:
                matrix.values[(i,j,k)] = (1,7)
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
