import heuristic

class DeleteIsolated(heuristic.Heuristic):
    
    def __init__(self, param):
        super(DeleteIsolated,self).__init__(param)
        
    """
    if a block does not have any block in his 26 block neighborhood, delete that block
    """
    def apply(self,world):
        
        matrix = world.matrix
        
        cells = matrix.values.keys()
        for (i,j,k) in cells:
            if matrix.neighbor_26((i,j,k)) == None:
                del matrix.values[(i,j,k)]
                
                            
        return world