import heuristic

class CreateWalls(heuristic.Heuristic):
    
    def __init__(self, param):
        super(CreateWalls,self).__init__(param)
        
    """
    If openStreetMap was used before, the program use building information to create walls for that area.
    If openStreetMap was not used before, the program create walls for the whole world. 
    If some building was inserted before from a binvox file, the program does not create walls in that area. 
    
    """
    def apply(self, world):
        h = 0
        
        
        
        matrix = world.matrix
        myBuildings = world.myBuildings
        green = world.green
        buildings = world.buildings
        
        if world.openStreetMap == False:
            buildings = [[True for j in range(matrix.resolution[0]+1)] for k in range(matrix.resolution[1]+1)]
    
        
        resolution = matrix.resolution
        for i in range(0,resolution[0]):
            for j in range(0,resolution[1]):
                h = 0
                if (myBuildings[i][j] == False) & ((green[i][j] == False) | (buildings[i][j])):
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
        return world