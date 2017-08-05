import heuristic

class SetGreenZone(heuristic.Heuristic):
    
    def __init__(self, param):
        super(SetGreenZone,self).__init__(param)
        
    """
    Change color to green in every block located in a green zone
    """
    def apply(self,world):
        
        if world.openStreetMap:
            matrix = world.matrix
            green = world.green
            
            for i in range(matrix.resolution[0]):
                for j in range(matrix.resolution[1]):
                    if green[i][j]:
                        for k in range(matrix.resolution[2]):
                            if (i,j,k) in matrix.values:
                                if matrix.values[(i,j,k)][1]<=16:
                                    matrix.values[(i,j,k)] = (1,16)
        return world