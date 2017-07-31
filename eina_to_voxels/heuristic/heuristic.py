
class Heuristic(object):
    
    
    def __init__(self, param):
        self.param = param


    def apply(self, world):
        raise NotImplementedError( "Should have implemented this" )

