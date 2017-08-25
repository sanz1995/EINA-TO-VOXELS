import heuristic

class DeleteIsolatedGroups(heuristic.Heuristic):
    
    def __init__(self, param):
        super(DeleteIsolatedGroups,self).__init__(param)
        
    """
    The program divides the space into groups of 9 with the same height. 
    If the average number of neighbors between them is low, delete the whole group.
    """
    def apply(self, world):
        #print "asdf"
        matrix = world.matrix
        buildings = world.buildings
        
        
        n = 3
        
        resolution = matrix.resolution
        
        x, y, z = resolution
        #cluster = [[[[] for i in range(z + 1)] for j in range(y/n + (y%n > 0))] for k in range(x/n + (x%n > 0))]
        #print "poiu"
        cellsByHeight = [[] for i in range(z + 1)]
        cells = matrix.values.keys()
        
        
        for (i,j,k) in cells:
            cellsByHeight[int(k)].append((i,j))
        
        #print "hola"
        neighborhood = []
        
        for r in range(0,resolution[2]):
            cluster = [[[] for j in range(y/n + (y%n > 0))] for k in range(x/n + (x%n > 0))]
            for (i,j) in cellsByHeight[r]:
                cluster[int(i/n)][int(j/n)].append((i,j,r))
                        
            for p in range(0,resolution[0]/n):
                for q in range(0,resolution[1]/n):
                    if buildings[p*n][q*n] == False:
                        value = 0
                        if len(cluster[p][q]) > 0:
                            if ((p == 0) | (p == resolution[0]/n-1) | (q == 0) | (q == resolution[1]/n-1)):
                                neighborhood = cluster[p][q]
                            else:
                                neighborhood = cluster[p][q] + cluster[p+1][q] + cluster[p-1][q] + cluster[p][q+1] + cluster[p][q-1]
                            for (i,j,k) in cluster[p][q]:
                                for h in range (1,5):
                                       
                                    if (i+h,j,k) in neighborhood:
                                        value += 1
                                    if (i-h,j,k) in neighborhood:
                                        value += 1
                                    if (i,j+h,k) in neighborhood:
                                        value += 1
                                    if (i,j-h,k) in neighborhood:
                                        value += 1
                            if (value/len(cluster[p][q]))<3:
                                for (i,j,k) in cluster[p][q]:
                                    del matrix.values[(i,j,k)]
                
        return world