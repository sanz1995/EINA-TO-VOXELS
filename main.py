import sys
import eina_to_voxels

if __name__ == '__main__':
    
    map = eina_to_voxels.Map()
    
    map.read(sys.argv[1])
    map.useOpenStreetMap()
    map.useHeuristic()
    
    #map.addBuilding(sys.argv[3],162,249,5)
    
    map.addBuilding(sys.argv[3],int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6]))
    
    map.addSign(226,263)
    
    matrix = map.createWalls()
    
    
    map.writeMatrix(sys.argv[2])
    
