import heuristic

class SetRoads(heuristic.Heuristic):
    
    def __init__(self, param):
        super(SetRoads,self).__init__(param)
        
    """
    Change the color to dark gray in every block located in a road
    """
    def apply(self,world):
        
        if world.openStreetMap:
            matrix = world.matrix
            roads = world.roads
            
            for i in range(matrix.resolution[0]):
                for j in range(matrix.resolution[1]):
                    if roads[i][j]:
                        for k in range(matrix.resolution[2]):
                            if (i,j,k) in matrix.values:
                                matrix.values[(i,j,k)] = (1,7)
        return world