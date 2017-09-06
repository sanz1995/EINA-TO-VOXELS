import sys
import eina_to_voxels

if __name__ == '__main__':
    
    if len(sys.argv) > 7:
        world = eina_to_voxels.World(sys.argv[1],sys.argv[7],float(sys.argv[8]),float(sys.argv[9]),float(sys.argv[10]), float(sys.argv[11]))
    else:
        world = eina_to_voxels.World(sys.argv[1],None,None,None,None,None)


    world.add(eina_to_voxels.UseOpenStreetMap([]))
    
    for i in range(0,3):
        world.add(eina_to_voxels.MergeColors([])) 
    
    world.add(eina_to_voxels.DeleteIsolated([]))
    
    for i in range(0,3):
        world.add(eina_to_voxels.DeleteIsolatedGroups([]))
        
    world.add(eina_to_voxels.ExpandBlocks([]))
    
    for i in range(0,15):
        world.add(eina_to_voxels.Join([7]))
    
    for i in range(0,5):
        world.add(eina_to_voxels.Join([]))
    
    world.add(eina_to_voxels.SetGreenZone([]))
    
    world.add(eina_to_voxels.SetRoads([]))
    
    world.add(eina_to_voxels.AddBuilding([sys.argv[3],float(sys.argv[4]),float(sys.argv[5]), float(sys.argv[6])]))    
    
    world.add(eina_to_voxels.CreateWalls([]))
    
    world.start()
    
    world.exportWorld(sys.argv[2])