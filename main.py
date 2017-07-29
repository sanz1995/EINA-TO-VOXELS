import sys
import eina_to_voxels
import time
import Image

if __name__ == '__main__':

    if sys.argv[1] == "split":
        eina_to_voxels.splitFile(sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6]),int(sys.argv[7]))
    else:
        world = eina_to_voxels.World()
        
        world.read(sys.argv[1])
        #world.readWithImage(sys.argv[1], "Resources/picture.jpg",671490.250, 4619729.750, 678750.250, 4614729.750)
            
        
        world.useOpenStreetMap()
        world.useHeuristic()
        
        world.addBuilding(sys.argv[3],float(sys.argv[4]),float(sys.argv[5]), float(sys.argv[6]))
        
        #world.addSign(675700,4616754, "Ada Byron.")
        world.createWalls()
        
        world.exportWorld(sys.argv[2])
        
    
    #print (time.time() - start)
