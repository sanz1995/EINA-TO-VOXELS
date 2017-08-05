class WorldDTO:
    
    def __init__(self, matrix, green, roads, buildings, myBuildings, openStreetMap):
        self.matrix = matrix
        self.green = green
        self.roads = roads
        self.buildings = buildings
        self.myBuildings = myBuildings
        self.openStreetMap = openStreetMap