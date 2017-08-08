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
        cluster = [[[[] for i in range(z + 1)] for j in range(y/n + (y%n > 0))] for k in range(x/n + (x%n > 0))]
        #print "poiu"
        cells = matrix.values.keys()
        for (i,j,k) in cells:
            cluster[int(i/n)][int(j/n)][int(k)].append((i,j,k))
        
        #print "hola"
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
                                
        #print "final"                       
        return world