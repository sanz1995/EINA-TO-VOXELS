import sys
import eina_to_voxels
#import time
#import Image

if __name__ == '__main__':
    
    #l = [[[0 for i in range(0,5)] for j in range(0,3)] for k in range(0,6)]
        
    
    if sys.argv[1] == "split":
        eina_to_voxels.splitFile(sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6]),int(sys.argv[7]))
    else:
        world = eina_to_voxels.World(sys.argv[1])
        world.add(eina_to_voxels.UseOpenStreetMap([]))
        
        for i in range(0,3):
            world.add(eina_to_voxels.MergeColors([])) 
        
        world.add(eina_to_voxels.DeleteIsolated([]))
        
        for i in range(0,1):
            world.add(eina_to_voxels.DeleteIsolatedGroups([]))
            
        
        world.add(eina_to_voxels.ExpandBlocks([]))
        
        
        for i in range(0,15):
            world.add(eina_to_voxels.Join([7]))
        
        for i in range(0,4):
            world.add(eina_to_voxels.Join([]))
            
        world.add(eina_to_voxels.SetGreenZone([]))
        world.add(eina_to_voxels.SetRoads([]))
        #world.add(eina_to_voxels.AddBuilding([sys.argv[3],float(sys.argv[4]),float(sys.argv[5]), float(sys.argv[6])]))    
            
        world.add(eina_to_voxels.CreateWalls([]))
        
        
        
        world.start()
        
        world.exportWorld(sys.argv[2])
        
    
    #print (time.time() - start)
