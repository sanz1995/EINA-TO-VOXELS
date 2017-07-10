import pointcloud_proc
import copy

"""

if a coordinate (i,y,k) with k < z is surrounded by 3 or more blocks, 
create a new block with the most common color between his neighbors. 
The program alse creates some trees if for blocks created in a green zone

"""
def join(matrix, z,green):
    new_matrix = pointcloud_proc.SparseMatrix(matrix.values, matrix.resolution, matrix.bcube)
    neighbor = 0
    neighbor_colors = [0]*20
    num = 0
    
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
                        if (neighbor_colors.index(max(neighbor_colors)) == 16) & green[i][j]:
                            num+=1
                            if num%30 == 0:
                                createTree(new_matrix,i,j,k)
                    neighbor_colors = [0]*20
                    neighbor = 0  
    return new_matrix




"""
Change the color tuple of each block depending on his neighbor
"""
def mergeColors(matrix):
    new_matrix = pointcloud_proc.SparseMatrix({}, matrix.resolution, matrix.bcube)
    neighbor_colors = [0]*20
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
                    neighbor_colors = [0]*20
                    new_score = neighbor_colors
    return new_matrix

"""
For each block, create 3 more blocks with the same color
"""
def expandBlocks(matrix):
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
                        
    return new_matrix


"""
if a block does not have any block in his 26 block neighborhood, delete that block
"""
def deleteIsolated(matrix):
    cells = matrix.values.keys()
    for (i,j,k) in cells:
        if pointcloud_proc.SparseMatrix.neighbor_26(matrix,(i,j,k)) == None:
            del matrix.values[(i,j,k)]
                        
    return matrix


"""
The program divides the space into groups of 9 with the same height. 
If the average number of neighbors between them is low, delete the whole group.
"""
def deleteIsolatedGroups(matrix,buildings):
    n = 3
    
    resolution = matrix.resolution
    
    x, y, z = resolution
    cluster = [[[[] for i in range(z + 1)] for j in range(y/n + (y%n > 0))] for k in range(x/n + (x%n > 0))]
    
    cells = matrix.values.keys()
    for (i,j,k) in cells:
        cluster[int(i/n)][int(j/n)][int(k)].append((i,j,k))
    
    
    neighborhood = []
    for p in range(0,resolution[0]/n):
        for q in range(0,resolution[1]/n):
            if buildings[p*n][q*n] == False:
                for r in range(0,resolution[2]):
                    value = 0
                    if len(cluster[p][q][r]) > 0:
                        if ((p == 0) | (p == resolution[0]/n-1) | (q == 0) | (q == resolution[1]/n-1)):
                            neighborhood = cluster[p][q][r]
                        else:
                            neighborhood = cluster[p][q][r] + cluster[p+1][q][r] + cluster[p-1][q][r] + cluster[p][q+1][r] + cluster[p][q-1][r]
                        for (i,j,k) in cluster[p][q][r]:
                            for h in range (1,5):
                                   
                                if (i+h,j,k) in neighborhood:
                                    value += 1
                                if (i-h,j,k) in neighborhood:
                                    value += 1
                                if (i,j+h,k) in neighborhood:
                                    value += 1
                                if (i,j-h,k) in neighborhood:
                                    value += 1
                        if (value/len(cluster[p][q][r]))<3:
                            for (i,j,k) in cluster[p][q][r]:
                                del matrix.values[(i,j,k)]
                            
                                     
    return matrix



"""
If two blocks share the same i and j value, create a column between them.
"""
def createWalls(matrix, myBuildings, buildings):
    
    h = 0
    
    resolution = matrix.resolution
    for i in range(0,resolution[0]):
        for j in range(0,resolution[1]):
            h = 0
            if (myBuildings[i][j] == False) & buildings[i][j]:
                for k in range(resolution[2],0,-1):
                    
                    if (i,j,k) in matrix.values:
                        
                        surrounded = ((i+1,j,k) in matrix.values) & ((i-1,j,k) in matrix.values) & ((i,j+1,k) in matrix.values) & ((i,j-1,k) in matrix.values)
                        if surrounded== False:
                            
                            ground = False
                            for h in range(0,k):
                                if ground == False:
                                    if (i,j,h) in matrix.values:
                                        ground = True
                                        g = h
                                else:
                                    if (k-h > 2) & (h-g > 2):
                                        if (h%4 != 0):
                                            matrix.values[(i,j,h)] = (1,8)
                                        else:
                                            matrix.values[(i,j,h)] = (1,20)
                                    else:
                                        matrix.values[(i,j,h)] = (1,8)
                        break
                

"""
Create a tree in the coordinates given
"""
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
    matrix.values[(x,y,z+10)] = (1,18)



"""
Change color to green in every block located in a green zone
"""
def setGreenZone(matrix,green):
    for i in range(matrix.resolution[0]):
        for j in range(matrix.resolution[1]):
            if green[i][j]:
                for k in range(matrix.resolution[2]):
                    if (i,j,k) in matrix.values:
                        matrix.values[(i,j,k)] = (1,16)
            


"""
Change the color to dark gray in every block located in a road
"""
def setRoads(matrix,roads):
    for i in range(matrix.resolution[0]):
        for j in range(matrix.resolution[1]):
            if roads[i][j]:
                for k in range(matrix.resolution[2]):
                    if (i,j,k) in matrix.values:
                        matrix.values[(i,j,k)] = (1,7)


