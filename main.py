import sys
import eina_to_voxels
import time

if __name__ == '__main__':
    
    if sys.argv[1] == "split":
        eina_to_voxels.splitFile(sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6]),int(sys.argv[7]))
    else:
        world = eina_to_voxels.World()
        world = eina_to_voxels.World()
        
        world.read(sys.argv[1])
        world.useOpenStreetMap()
        world.useHeuristic()
        
        
        world.addBuilding(sys.argv[3],int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6]))
        
        #map.addSign(226,263)
        
        world.createWalls()
        
        world.exportWorld(sys.argv[2])
    
    #print (time.time() - start)
