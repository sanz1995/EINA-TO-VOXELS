class WorldDTO:
    
    def __init__(self, matrix):
        self.matrix = matrix
        
        resolution = matrix.resolution
        
        self.myBuildings = [[False for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
        
        self.green = [[False for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
        
        self.roads = [[False for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
    
        self.buildings = [[False for j in range(resolution[0]+1)] for k in range(resolution[1]+1)]
        
        
        self.openStreetMap = False