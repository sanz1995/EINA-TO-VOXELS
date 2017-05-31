#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pointcloud_proc.py - Point cloud processing.
# Copyright (C) 2017 Rubén Béjar {http://www.rubenbejar.com/}
   

import argparse
import math
import time
import sys
#import chull

"""
In this module:

resolution: a tuple with three integers: number of cells in X, Y, Z 
(ncells_x, ncells_y, ncells_z)
resolution usually refers to a 3d grid we use to divide the volume
of interest in discrete, equally-sized cuboids 
(<https://en.wikipedia.org/wiki/Cuboid>) 

bounding cube (bcube): the min and max corners of a cuboid (extremes 
in a # maximum diagonal) implemented 
as tuples of three floats (x,y,z) and contained in a dictionary
{'min': (x,y,z), 'max': (x,y,z)}

min and max corners refers to a couple of the farthest corners (maximum
diagonal) of a cuboid where min is one with the minimum sum of 
(x,y,z) and max is one with the maximum sum of (x,y,z).  

cell: a tuple with three integers which identify one cell in
a volume gridded with a certain resolution. 
(i, j, k) where i is in [0..X_resolution-1], j in [0..Y_resolution-1]
and k in [0..Z_resolution-1]

coord: a tuple with three floats (x,y,z). It is a 3D point.

cluster (of cells): a set of contiguous cells (6-neighborhood)
"""


class SparseMatrix():
    """
    A sparse matrix representing a gridded volume. This volume
    is bounded by a bcube and the resolution of the grid is
    given by resolution.
    
    values is a dictionary indexed by 3-tuples of integers 
    {(i,j,k):value} where value is an integer. 
    Typically this integer is the number of points
    included in the cell, but it can be used also as an id. 
    Cells with a zero (zero points, no id etc.) do not have an
    entry in this dictionary.
             
    resolution and bcube play the same role as in the rest of the module
    """
    def __init__(self, values, resolution, bcube):
        self.values = values
        self.resolution = resolution
        self.bcube = bcube
    
    # This is an idiomatic way to do an "alternate constructor" in
    # Python as far as I know
    @classmethod
    def create_from_coords(cls, coords_iterator, resolution, bcube):
        """
        Reads a coords_iterator and produces a SparseMatrix of the given
        resolution. In each cell there will
        be the number of points in the coords_iterator that fall in that
        cell.
         
        @param coords_iterator: an iterator which produces tuples (x,y,z) (floats)    
        @param resolution: (ncells_x, ncells_y, ncells_z) (are integers)
        @param bcube: bounding cube {'min': (x,y,z), 'max': (x,y,z)} (are floats)  
    
        @return: a sparse matrix with a field named values that is a 
                 dictionary indexed by 3-tuples of integers 
                 {(x,y,z):nPoints}  Cells with zero points do not have an entry in this
                 dictionary
        """
    
        matrix = SparseMatrix({}, resolution, bcube)        
        for coords in coords_iterator:
            ncell = coords_to_cell(coords, resolution, bcube)
            #print(ncell)
            if ncell in matrix.values:
                matrix.values[ncell] += 1
            else:
                matrix.values[ncell] = 1
        return matrix
    
    def neighbor_26(self, cell):
        """
        Returns the value of the first found 26-neighbor (or 3D Moore 
        neighborhood) of a cell in this SparseMatrix. None if no one found. 
        """
        x,y,z = cell
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                for k in [-1, 0, 1]:
                    if not (i == 0 and j == 0 and k == 0):                    
                        if (x+i, y+j, z+k) in self.values:
                            return self.values[(x+i, y+j, z+k)]
        return None  
    def neighbor_6(self, cell):
        """
        Returns the value of the first found 6-neighbor (3D Von Neumann
        neighborhood) of a cell in a SparseMatrix. None if no one found.
    
        NOT TESTED CAREFULLY YET
        """
        x,y,z = cell
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                for k in [-1, 0, 1]:
                    if (abs(i)+abs(j)+abs(k) == 1):                                        
                        if (x+i, y+j, z+k) in self.values:
                            return self.values[(x+i, y+j, z+k)]
        return None       
        
        
      
         
def calculate_cell_size(resolution, bcube):
    """
    Given a resolution and a bounding cube, it returns the size of each
    cell in the units of the bounding cube.
    """
    minx, miny, minz = bcube['min']
    maxx, maxy, maxz = bcube['max']
    
    return ((maxx - minx) / resolution[0],
            (maxy - miny) / resolution[1],
            (maxz - minz) / resolution[2])    
         
def cell_to_coords(cell, resolution, bcube):
    """
    Given a cell in a bcube of the given resolution,
    it returns the min and max corners of that cell 
    as coordinates in the system of coordinates of bcube
    as a tuple of six floats (xmin,ymin,zmin,xmax,ymax,zmax)    
    """
    i,j,k = cell
    
    minx, miny, minz = bcube['min']
    maxx, maxy, maxz = bcube['max']
    
    cell_size = calculate_cell_size(resolution, bcube)
    
    x1 = minx + i * cell_size[0]
    y1 = miny + j * cell_size[1]
    z1 = minz + k * cell_size[2]
    
    x2 = x1 + cell_size[0]
    y2 = y1 + cell_size[1]
    z2 = z1 + cell_size[2]
    
    # If we have something barely out of our bcube 
    # may be a rounding error or just that we have a
    # point in the limit. We have to
    # keep it inside...
    # Warning! This may hide other errors. A better solution
    # would be defining a tolerance or an "inner margin"...
        
    x2 = x2 if x2 <= maxx else maxx
    y2 = y2 if y2 <= maxy else maxy
    z2 = z2 if z2 <= maxz else maxz
             
    
    assert(x1 >= minx and x1 <= maxx)
    assert(y1 >= miny and y1 <= maxy)
    assert(z1 >= minz and z1 <= maxz)
    
    assert(x2 >= minx and x2 <= maxx)
    assert(y2 >= miny and y2 <= maxy)
    assert(z2 >= minz and z2 <= maxz)
    
    return (x1,y1,z1,x2,y2,z2)


def coords_to_cell(coords, resolution, bcube):
    """
    Given coords (a tuple of (x,y,z) floats) inside a 
    bcube of the given resolution, it returns
    the cell occupied by those coords as a tuple
    of three integers (i,j,k)
    """
    x,y,z = coords
    minx, miny, minz = bcube['min']
    maxx, maxy, maxz = bcube['max']
    #print(x)
    #print(minx)
    #print("----------")
    assert(x >= minx and x <= maxx)
    assert(y >= miny and y <= maxy)
    assert(z >= minz and z <= maxz)
                   
    cell_size = ((maxx - minx) / resolution[0],
                 (maxy - miny) / resolution[1],
                 (maxz - minz) / resolution[2])
    #print(cell_size)
    #print(cell_size)
    # If we have something barely out of our cells, it 
    # may be a rounding error or just that we have a
    # point in the limit of a cell etc. We have to
    # keep it inside...
    # Warning! This may hide other errors. A better solution
    # would be defining a tolerance or an "inner margin"...
    
    n0 = (x - minx) // cell_size[0]
    n1 = (y - miny) // cell_size[1]
    n2 = (z - minz) // cell_size[2]        
    
    ncell = (n0 if n0 < resolution[0] else n0 - 1,
             n1 if n1 < resolution[1] else n1 - 1,
             n2 if n2 < resolution[2] else n2 - 1)
    
    #print(ncell)
    assert(ncell[0] >= 0 and ncell[0] < resolution[0])
    assert(ncell[1] >= 0 and ncell[1] < resolution[1])
    assert(ncell[2] >= 0 and ncell[2] < resolution[2])
    
    return ncell        

def min_max_cells(cells):
    """
    Takes a list of cells and returns the min and max cells 
    as a 6-tuple of integers (min_i, min_j, min_k, max_i, max_j, max_k)
    of the minimum "box" that would contain all those cells    
    """
    assert(len(cells) > 0)
    curr_max = [0,0,0]
    curr_min = [sys.maxsize, sys.maxsize, sys.maxsize]
    for cell in cells:
        if cell[0] < curr_min[0]:
            curr_min[0] = cell[0]
        if cell[1] < curr_min[1]:
            curr_min[1] = cell[1]
        if cell[2] < curr_min[2]:
            curr_min[2] = cell[2]
        
        if cell[0] > curr_max[0]:
            curr_max[0] = cell[0]
        if cell[1] > curr_max[1]:
            curr_max[1] = cell[1]
        if cell[2] > curr_max[2]:
            curr_max[2] = cell[2]
    return tuple(curr_min + curr_max)    
   
def cluster_matrix_from_cell_matrix(matrix):
    """
    Takes a SparseMatrix, and creates another SparseMatrix
    where each cell is given an id. Neighbors in the
    input matrix will be given the same id (i.e., they are
    clustered by 6-adjacency). It also creates a list indexed by
    the cluster ids, where each entry is a list of cells in that
    cluster. 
    
    @returns: (clustered SparseMatrix, cluster list)
    """
    clusters = SparseMatrix({}, matrix.resolution, matrix.bcube)      
    cluster_list = []        
    latest_cluster_id = -1
    
    # Clusterización de celdas que están juntas. 
    # Creamos clusters asociando 
    # a cada grupo de celdas continuas de matrix un id y guardando estos
    # ids en clusters para cada celda ({(x,y,z):cluster_id}) 
    # Al final en clusters habrá las mismas entradas que
    # en matrix, pero con tantos ids como clusters hayamos encontrado
  
    # Tengo que recorrer la matriz en orden, porque si voy
    # dando saltos, habrá clusteres que no reconoceré como tales
    # (si veo el 1, y luego el 3, los clasifico como separados,
    # pero si hay un 2 por medio y no lo veo hasta el final resulta
    # que eran un cluster). A lo mejor sería menos costoso 
    # ordenar por las claves del diccionario matrix.values...

    for i in range(matrix.resolution[0]):
        for j in range(matrix.resolution[1]):
            for k in range(matrix.resolution[2]):
                ncell = (i,j,k)
                #print(ncell)
                if ncell in matrix.values:                   
                    neighbor_id = clusters.neighbor_6(ncell) 
                    if neighbor_id:
                        clusters.values[ncell] = neighbor_id
                        cluster_list[neighbor_id].append(ncell)
                    else:
                        latest_cluster_id += 1
                        clusters.values[ncell] = latest_cluster_id
                        # We assume that the cluster ids are consecutive numbers!
                        cluster_list.append([ncell])      
    return (clusters, cluster_list)

def are_full_box(cells, min_cell, max_cell):
    """
    Returns True if and only if there is a cell
    in the list cells for each cell inside the 
    "box" defined by the corners min_cell and 
    max_cell
    """
    for i in range(min_cell[0], max_cell[0] + 1):
        for j in range(min_cell[1], max_cell[1] + 1):
            for k in range(min_cell[2], max_cell[2] + 1):
                if not ((i,j,k) in cells):
                    return False
    return True

def are_empty_box(cells, min_cell, max_cell):
    """
    Returns True if and only if there is not
    a single cell in the list cells inside the 
    "box" defined by the corners min_cell and 
    max_cell
    """
    for i in range(min_cell[0], max_cell[0] + 1):
        for j in range(min_cell[1], max_cell[1] + 1):
            for k in range(min_cell[2], max_cell[2] + 1):
                if (i,j,k) in cells:
                    return False
    return True


def cells_to_boxes(cells, min_cell, max_cell):
    """
    Takes a list of cells, wich must be inside
    the "box" defined by the corners
    min_cell and max_cell, and returns
    a list of full boxes created "melding" cells
    in the list. 
    
    The strategy used is not optimal, but should be good enough and fast: the cells
    are subdivided in eight: if any of those divisions are a full box, then
    that will be returned; if not, it will be subdivided again...
    @param cells: [(i,j,k),(l,m,n)...] where i,j... are positive integers
    @param min_cell and max_cell: e.g. (i,j,k) where i,j,... are positive integers
    """    
    min_i = min_cell[0]
    max_i = max_cell[0]
    med_i = min_i +((max_i - min_i) // 2)  
    
    min_j = min_cell[1]
    max_j = max_cell[1]
    med_j = min_j +((max_j - min_j) // 2)
    
    min_k = min_cell[2]
    max_k = max_cell[2]
    med_k = min_k+((max_k - min_k) // 2)
    
    if (max_cell[0] > min_cell[0] and max_cell[1] > min_cell[1] and
        max_cell[2] > min_cell[2]):
        # We can divide in eight cubes
        ncubes = [(min_i, min_j, min_k, med_i, med_j, med_k),
                  (med_i + 1, min_j, min_k, max_i, med_j, med_k),
                  (med_i + 1, med_j + 1, min_k, max_i, max_j, med_k),
                  (min_i, med_j + 1, min_k, med_i, max_j, med_k),         
                  (min_i, min_j, med_k + 1, med_i, med_j, max_k),
                  (med_i + 1, min_j, med_k + 1, max_i, med_j, max_k),
                  (med_i + 1, med_j + 1, med_k + 1, max_i, max_j, max_k),
                  (min_i, med_j + 1, med_k + 1, med_i, max_j, max_k)]
    elif (max_cell[0] == min_cell[0] and max_cell[1] == min_cell[1] and
        max_cell[2] == min_cell[2]):
        # A single cell, no divisions left
        ncubes = [(min_i, min_j, min_k, max_i, max_j, max_k)]
    # In any other case, we divide in two (we could divide in four in some
    # cases, still not sure about the tradeoffs)
    elif (max_cell[0] > min_cell[0]):
        # Divide in two
        ncubes = [(min_i, min_j, min_k, med_i, max_j, max_k),
                  (med_i + 1, min_j, min_k, max_i, max_j, max_k)]
    elif (max_cell[1] > min_cell[1]):
        # Divide in two
        ncubes = [(min_i, min_j, min_k, max_i, med_j, max_k),
                  (min_i, med_j + 1, min_k, max_i, max_j, max_k)]    
    elif (max_cell[2] > min_cell[2]):
        # Divide in two
        ncubes = [(min_i, min_j, min_k, max_i, max_j, med_k),
                  (min_i, min_j, med_k + 1, max_i, max_j, max_k)] 
    else:
        # We should not be here
        raise Exception("Unable to subdivide cells. This should not happen")
    
    cube_list = []    
    for cube in ncubes:
        min_c = (cube[0],cube[1],cube[2])
        max_c = (cube[3],cube[4],cube[5])
        if are_full_box(cells, min_c, max_c):            
            cube_list.append(cube)
        elif not are_empty_box(cells, min_c, max_c):                    
            cube_list.extend(cells_to_boxes(cells, min_c, max_c))        
         
    return cube_list
                  
    
#def cluster_to_convex_hull(cluster, resolution, bcube):
    """
    Takes a "cluster" (a list of contiguous cells (6-neighbours)
    with at least one cell) and returns
    the convex hull of those cells in the given resolution grid of bcube.
    """
    """    
    assert(len(cluster) > 0)            
    points_list = []
    for cell in cluster:
        bounding_coords = cell_to_coords(cell, resolution, bcube)
        #Though adding every corner of each cell should not be necessary,
        #and will be slower, it is a safe and simple way to prevent having 
        #only coplanar points in any conceivable circumstance
        points_list.append(chull.Vector(bounding_coords[0], 
                                           bounding_coords[1], 
                                           bounding_coords[2]))
        points_list.append(chull.Vector(bounding_coords[3], 
                                           bounding_coords[1], 
                                           bounding_coords[2]))
        points_list.append(chull.Vector(bounding_coords[0], 
                                           bounding_coords[4], 
                                           bounding_coords[2]))
        points_list.append(chull.Vector(bounding_coords[0], 
                                           bounding_coords[1], 
                                           bounding_coords[5]))
        points_list.append(chull.Vector(bounding_coords[3], 
                                           bounding_coords[4], 
                                           bounding_coords[5]))
        points_list.append(chull.Vector(bounding_coords[3], 
                                           bounding_coords[4], 
                                           bounding_coords[2]))
        points_list.append(chull.Vector(bounding_coords[0], 
                                           bounding_coords[4], 
                                           bounding_coords[5]))
        points_list.append(chull.Vector(bounding_coords[3], 
                                           bounding_coords[1], 
                                           bounding_coords[5]))
        
    return chull.Hull(points_list)"""
    

def cells_to_POV(cluster_list, matrix, filepath, tolerance, 
                    min_cluster_size, cell_type, point_size,
                    meld_boxes):
    """
    Takes a list of cell clusters (created from matrix),
    and creates a text file with POV syntax.
    
    If cell_type is "box", it will create a union of cubes
    per cluster with more than min_cluster_size cells. There will be a 
    cube per each cell with more than tolerance points 
    in it (number of points per cell must be in matrix). If meld_boxes
    is true, it will try to create bigger cubes melding together
    contiguous cells.
    
    If point_size is provided, the cells will be filled with objects
    of this size at their centers.
    
    This function assumes that coords in matrix are (lon, lat, height) so
    it will produce (lon, height, lat) when writing to POV file, in order
    to follow POV axis conventions as OSM2POV does.
    """
    
    f = open(filepath,'w')
    if point_size:
        cell_size = [point_size, point_size, point_size]
    else:
        cell_size = calculate_cell_size(matrix.resolution, matrix.bcube)
        
        # Not always needed, but it is just a harmless line of text if not used...
    f.write('#declare cell_size=<{0:.2f},{1:.2f},{2:.2f}>;\n'.format(
      cell_size[0], cell_size[2], cell_size[1]))    
    
    
    for cluster in cluster_list:
        if len(cluster) > min_cluster_size:
            cells_in_tolerance = [cell for cell in cluster if matrix.values[cell] > tolerance]
            # If after removing those cells with not enough points in them the cluster
            # is smaller than min_cluster_size, we will not process it
            if (len(cells_in_tolerance) > min_cluster_size):
                if meld_boxes:
                    corners = min_max_cells(cells_in_tolerance)
                    boxes = cells_to_boxes(cells_in_tolerance, corners[:3], corners[3:])
                    for box in boxes:
                        mincoords = cell_to_coords(box[:3], matrix.resolution, matrix.bcube)
                        maxcoords = cell_to_coords(box[3:], matrix.resolution, matrix.bcube)
                        if cell_type == "sphere":
                            f.write('  sphere {0, 0.5\n')
                            # radius is 0.5, so we can scale with the cell_size
                            # and have a spheroid covering the whole cell
                            f.write('    scale cell_size\n')   # Scale before translate!
                            f.write('    translate <{0:.2f},{1:.2f},{2:.2f}>\n'.format(
                              mincoords[0]+(maxcoords[3]-mincoords[0])/2,                     
                              mincoords[2]+(maxcoords[5]-mincoords[2])/2, 
                              mincoords[1]+(maxcoords[4]-mincoords[1])/2))                                                                
                        elif cell_type == "box":
                            f.write('  box {{<{0:.2f},{1:.2f},{2:.2f}>,<{3:.2f},{4:.2f},{5:.2f}>\n'.format(
                              mincoords[0],mincoords[2],mincoords[1],maxcoords[3],maxcoords[5],maxcoords[4]))
                        elif cell_type == "cylinder":
                            f.write('  cylinder {<0,-0.5,0>, <0,0.5,0>, 0.5\n')
                            f.write('    scale cell_size\n')   # Scale before translate!
                            f.write('    translate <{0:.2f},{1:.2f},{2:.2f}>\n'.format(
                              mincoords[0]+(maxcoords[3]-mincoords[0])/2,                     
                              mincoords[2]+(maxcoords[5]-mincoords[2])/2, 
                              mincoords[1]+(maxcoords[4]-mincoords[1])/2))
                        elif cell_type == "cyl-blob":
                            f.write('  cylinder {<0,-0.5,0>, <0,0.5,0>, 0.5, 1\n')
                            f.write('    scale cell_size*<2,1,2>\n')   # Scale before translate!
                            f.write('    translate <{0:.2f},{1:.2f},{2:.2f}>\n'.format(
                              mincoords[0]+(maxcoords[3]-mincoords[0])/2,                     
                              mincoords[2]+(maxcoords[5]-mincoords[2])/2, 
                              mincoords[1]+(maxcoords[4]-mincoords[1])/2))                            
                        else:
                            raise ValueError("cell_type " + cell_type + " is not valid for POV output when melding cells")
                        f.write('  texture {texture_VOXEL}\n')
                        # Using no_shadow prevents the "voxels" from casting shadows
                        # If this is or not useful, will depende on the final illumination
                        # of the scene
                        #f.write('  no_shadow\n')
                        f.write('}\n')                            
                else:
                    # NO MELDING...
                    if cell_type == "cyl-blob":
                        f.write('blob {\n')
                        f.write('  threshold 0.6')
                    else:
                        f.write('union {\n')
                    for cell in cells_in_tolerance:
                        coords = cell_to_coords(cell, matrix.resolution, matrix.bcube)
                        if cell_type == "box":
                            f.write('  box {{<{0:.2f},{1:.2f},{2:.2f}>,<{3:.2f},{4:.2f},{5:.2f}>}}\n'.format(
                              coords[0],coords[2],coords[1],coords[3],coords[5],coords[4]))
                        elif cell_type == "sphere":
                            f.write('  sphere {0, 0.5\n')
                            # radius is 0.5, so we can scale with the cell_size
                            # and have a spheroid covering the whole cell
                            f.write('    scale cell_size\n')   # Scale before translate!
                            f.write('    translate <{0:.2f},{1:.2f},{2:.2f}>}}\n'.format(
                              coords[0]+(coords[3]-coords[0])/2,                     
                              coords[2]+(coords[5]-coords[2])/2, 
                              coords[1]+(coords[4]-coords[1])/2))    
                        else:
                            raise ValueError("cell_type " + cell_type + " is not valid for POV output when not melding cells")       
                    f.write('  texture {texture_VOXEL}\n')
                    # Using no_shadow prevents the "voxels" from casting shadows
                    # If this is or not useful, will depende on the final illumination
                    # of the scene
                    #f.write('  no_shadow\n')
                    f.write('}\n')                            
    f.close()
    
def cells_to_Threejs(cluster_list, matrix, filepath, tolerance, 
                        min_cluster_size, cell_type, point_size, 
                        meld_boxes):
    """
    Takes a list of cell clusters (created from matrix),
    and creates a JS file with Three.js syntax.
    
    If cell_type is "box", it will create a number of cubes
    per cluster with more than min_cluster_size cells. There will be a 
    cube per each cell with more than tolerance points 
    in it (this information is contained in matrix). If meld_boxes
    is true, it will try to create bigger cubes melding together
    contiguous cells.
    
    If point_size is provided, the cells will be filled with objects
    of this size at their centers.
    
    This function assumes that coords in matrix are (lon, lat, height) so
    it will produce (lon, height, -lat) when writing to Threejs file, in order
    to follow its axis conventions.
    """
    #print("hola")
    f = open(filepath,'w')
    
    f.write('// tolerance = {}\n'.format(tolerance))
    f.write('// min_cluster_size = {}\n'.format(min_cluster_size))
    f.write('// cell_type = {}\n'.format(cell_type))
    f.write('// meld_boxes = {}\n'.format(meld_boxes))
    f.write('// matrix.resolution = {}\n'.format(matrix.resolution))
    f.write('// matrix.bcube = {}\n'.format(matrix.bcube))
    
       
    f.write('function RichPanoramaGrid() {\n')
    f.write('  var RPG = {};\n')
    
    if point_size:
        cell_size = [point_size, point_size, point_size]
    else:
        cell_size = calculate_cell_size(matrix.resolution, matrix.bcube)
    if cell_type == "box":
        f.write('  RPG.cellGeometry = new THREE.CubeGeometry({0:.2f},{1:.2f},{2:.2f});\n'.format(
          cell_size[0], cell_size[2], cell_size[1]))
    elif cell_type == "sphere":
        pass
        # Maybe one day I will implement this...
    f.write('  RPG.cellPositions = new Array();\n')
    if meld_boxes:
        f.write('  RPG.uniformSizeCells = false;\n')
        f.write('  RPG.cellSizes = new Array();\n')    
    else:
        f.write('  RPG.uniformSizeCells = true;\n')
        
    #print("hola1")
    for cluster in cluster_list:
        if len(cluster) > min_cluster_size:
            #print("hola2")
            cells_in_tolerance = [cell for cell in cluster if matrix.values[cell] > tolerance]
            # If after removing those cells with not enough points in them the cluster
            # is smaller than min_cluster_size, we will not process it
            if (len(cells_in_tolerance) > min_cluster_size):  
                print("hola3")
                #print(len(cells_in_tolerance))          
                if meld_boxes:
                    #print("hola4")
                    corners = min_max_cells(cells_in_tolerance)
                    boxes = cells_to_boxes(cells_in_tolerance, corners[:3], corners[3:])
                    for box in boxes:
                        print("hola5")
                        mincoords = cell_to_coords(box[:3], matrix.resolution, matrix.bcube)
                        maxcoords = cell_to_coords(box[3:], matrix.resolution, matrix.bcube)
                        if cell_type == "box":
                            #print("hola6")
                            f.write('  RPG.cellPositions.push({{x:{0:.2f}, y:{1:.2f}, z:{2:.2f}}});\n'.format(
                              mincoords[0]+(maxcoords[3]-mincoords[0])/2,                     
                              mincoords[2]+(maxcoords[5]-mincoords[2])/2, 
                              -(mincoords[1]+(maxcoords[4]-mincoords[1])/2)))
                            f.write('  RPG.cellSizes.push({{x:{0:.2f}, y:{1:.2f}, z:{2:.2f}}});\n'.format(
                              box[3]-box[0]+1,
                              box[5]-box[2]+1,
                              box[4]-box[1]+1))
                        else:
                            print("error")
                            raise ValueError("cell_type " + cell_type + " is not valid for Three.js output")                                        
                else:
                    for cell in cells_in_tolerance:
                        print("hola7")
                        coords = cell_to_coords(cell, matrix.resolution, matrix.bcube)
                        if cell_type == "box":
                            #print("hola8")
                            f.write('  RPG.cellPositions.push({{x:{0:.2f}, y:{1:.2f}, z:{2:.2f}}});\n'.format(
                              coords[0]+(coords[3]-coords[0])/2,                     
                              coords[2]+(coords[5]-coords[2])/2, 
                              -(coords[1]+(coords[4]-coords[1])/2)))
                        else:
                            raise ValueError("cell_type " + cell_type + " is not valid for Three.js output")                                        
    f.write('  return RPG;\n')
    f.write('};\n')   
    f.write('var richPanoramaGrid = RichPanoramaGrid();\n')     
    f.close()
    

# Warning! This procedure creates really big POV files, which render
# really slowly, if coords_iterator has a moderately big size (e.g.
# 10M points create a 1.1GB POV file with a rendering time close
# to half an hour). The resulting rendered image will not have a 
# substantially better quality than the "gridded" version produced
# by cells_to_POV with a moderate resolution
def points_to_POV(coords_iterator, filepath, point_size, cell_type):
    f = open(filepath,'w')
    if cell_type == "cyl-blob":
        f.write('blob {\n')
        f.write('  threshold 0.6')
    else:
        f.write('union {\n')
    half_point_size = point_size / 2
    for coords in coords_iterator:
        x,y,z = coords
        if cell_type == "sphere":
            f.write('  sphere {0, 0.5\n')
            # radius is 0.5, so we can scale with the point_size
            f.write('    scale {0}\n'.format(point_size))   # Scale before translate!
            f.write('    translate <{0:.2f},{1:.2f},{2:.2f}>\n'.format(x, z, y))
            f.write('}\n')                                    
        elif cell_type == "box":  
            f.write('  box {{<{0:.2f},{1:.2f},{2:.2f}>,'+
                            '<{3:.2f},{4:.2f},{5:.2f}>}}\n'.format(
              x - half_point_size, z - half_point_size, y - half_point_size,
              x + half_point_size, z + half_point_size, y + half_point_size))
        elif cell_type == "cylinder":
            f.write('  cylinder {<0,-0.5,0>, <0,0.5,0>, 0.5\n')
            f.write('    scale {0}\n'.format(point_size))   # Scale before translate!
            f.write('    translate <{0:.2f},{1:.2f},{2:.2f}>\n'.format(x,z,y))
            f.write('}\n')
        elif cell_type == "cyl-blob":
            f.write('  cylinder {<0,-0.5,0>, <0,0.5,0>, 0.5, 1\n')
            f.write('    scale {0}*<2,1,2>\n'.format(point_size))   # Scale before translate!
            f.write('    translate <{0:.2f},{1:.2f},{2:.2f}>\n'.format(x,z,y))
            f.write('}\n')
        else:
            raise ValueError("cell_type " + cell_type + " is not valid")
    f.write('  texture {texture_POINT}\n')
    # Using no_shadow prevents the points from casting shadows
    # If this is or not useful, will depend on the final illumination
    # of the scene
    f.write('  no_shadow\n')
    f.write('}\n')                            
    f.close()

# Inspired by a similar code in OSM2POV
# origin_lat and origin_lon must be the center of the sdata bounding box
# tests de ZGZ-Actur: origin_lat = 41.6661;  origin_lon = -0.89047
def hack_map_projection(lon, lat, origin_lon, origin_lat):
    """
    Takes a pair of spherical coordinates (longitude, latitude) and
    an arbitray origin in spherical coordinates too (origin_lon, origin_lat)
    and returns a pair of euclidean (i.e. planar) coordinates in
    meters as a tuple of floats (x,y) relative to origin_lon and origin_lat
    that will be 0,0.
    
    It is only an approximation, not a true map projection.
    """
    lon_correction = 1.5
    r_major = 6378137.0
    
    def lon_to_x(lon):
        return r_major * math.radians(lon);
    def lat_to_y(lat):
        return r_major * math.log(math.tan(math.pi/4+math.radians(lat)/2))
        
    x = lon_to_x(lon - origin_lon) / lon_correction
    y = lat_to_y(lat - origin_lat)
    return (x,y)

# Besides applying the hack map projection, we must take into consideration
# that coordinates in POV are not in the same order X is LON, Y is HEIGHT,
# Z is LAT
# We also normalize heights so they start in zero
def coords_to_hack_map_proj(coords, origin_lon, origin_lat, min_height):
    """
    @param coords: (lon, lat, height)
    @return: (lon, lat, height) reprojected with hack_map_projection. 
    Heights are normalized so they start in zero 
    """
    x,y = hack_map_projection(coords[0], coords[1], origin_lon, origin_lat)
    return (x, y, coords[2] - min_height)

def coords_in_bcube(coords, bcube):
    """
    True if and only if coords inside bcube
    """
    return (coords[0] >= bcube[0] and coords[0] <= bcube[3] and
            coords[1] >= bcube[1] and coords[1] <= bcube[4] and
            coords[2] >= bcube[2] and coords[2] <= bcube[5])

def simple_text_file_generator(filepath, coord_filter = lambda coords: True,
                               coord_transformer = lambda coords: coords):
    """
    Iterates over a text file composed of N lines with X Y Z producing
    tuples (X,Y,Z), where X,Y and Z are already converted to float numbers
    
    coord_filter may be used to discard some coords for any reason. By
    default all coords are used
    
    coord_transformer will possibly be a coord reprojector, and is used
    on every tuple of coords read before yielding it. By default
    it does nothing to the coords 
    """
    # The use of with makes sure that the file will be closed in the end
    with open(filepath,'r') as f:
        for line in f:        
            coords = [float(coord) for coord in line.split()]
            if coord_filter(coords):                        
                yield coord_transformer(coords)        

def main():
    init_time = time.time()
    parser = argparse.ArgumentParser(description="Process cloud point file. BE CAREFUL, NOT EVERY"+
                                     " PARAMETER COMBINATION IS IMPLEMENTED, EVEN IF IT WOULD MAKE SENSE")
    
    parser.add_argument("input_file", help="The input file")
    parser.add_argument("output_file",help="The output file")
        
    parser.add_argument("--origin-lon", dest="origin_lon", type=float, default="0.0",
                      help="LONGITUDE for the center of the world", metavar="LONGITUDE")
    parser.add_argument("--origin-lat", dest="origin_lat", type=float, default="0.0",
                      help="LATITUDE for the center of the world", metavar="LATITUDE")
    parser.add_argument("--bcube", dest="bcube", type=float, nargs=6, 
                        default=(-1.0, -1.0, -1.0, 1.0, 1.0, 1.0), 
                        metavar=("LON-MIN", "LAT-MIN", "HEIGHT-MIN", 
                                 "LON-MAX", "LAT-MAX", "HEIGHT-MAX"), 
                        help="Bounding cube of the world")    
    parser.add_argument("--inner-bcube", dest="inner_bcube", type=float, nargs=6,                         
                        metavar=("LON-MIN", "LAT-MIN", "HEIGHT-MIN", 
                                 "LON-MAX", "LAT-MAX", "HEIGHT-MAX"), 
                        help="Only the points in this bounding cube, must be inside the bounding"+ 
                             " cube of the world will be considered")
    parser.add_argument("--resolution", dest="resolution", type=int, nargs=3, 
                        metavar=("LON-RES", "LAT-RES", "HEIGHT-RES"), 
                        help="Use a 3d grid of the given resolution as output to render the points")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--point-size", dest="point_size", type=float,                          
                        metavar=("POINT-SIZE"), 
                        help="Use an element of the given size as output to render the points (if alone) or the cells (if along with --resolution)")
    group.add_argument("--meld-boxes", dest="meld_boxes", action="store_true",
                        help="If creating boxes filling the cells, it will try to minimize"+
                        " the total number of boxes by melding together contiguous cells into bigger boxes")
    
    parser.add_argument("--output-format", dest="output_format", choices=["pov", "threejs"],  
                        default="pov",                          
                        help="Output format: POV-RAY or Three.js compatible JavaScript")            
    parser.add_argument("--tolerance", dest="tolerance", type=int,  
                        default=1, metavar="TOLERANCE",                         
                        help="More than TOLERANCE points in a cell to consider it occupied")        
    parser.add_argument("--min-cluster-size", dest="min_cluster_size", type=int,  
                        default=1, metavar="MIN-CLUSTER-SIZE",                         
                        help="More than MIN-CLUSTER-SIZE cells in a cluster to render it")
    parser.add_argument("--cell-type", dest="cell_type", choices=["box", "sphere", 
                                                                  "cylinder", "cyl-blob"],
                        default="box",                                                          
                        help="Choose the type of primitive for the output")
    parser.add_argument("--verbose", action="store_true",
                       help="Writes some statistics to the output")

    
    args = parser.parse_args()
    
    # Reproject bcube to POV hack map
    minbcube = coords_to_hack_map_proj(args.bcube[:3], args.origin_lon, 
                                       args.origin_lat, args.bcube[2])
    maxbcube = coords_to_hack_map_proj(args.bcube[3:], args.origin_lon, 
                                       args.origin_lat, args.bcube[2])    
    assert(maxbcube[0] >= minbcube[0] and
           maxbcube[1] >= minbcube[1] and
           maxbcube[2] >= minbcube[2])
    
    # If we are creating a grid with the points (i.e. creating an
    # object per cell in this grid, that may contain many points)
    if args.resolution:
        if args.inner_bcube:
            coord_filter = lambda coords: coords_in_bcube(coords, args.inner_bcube)
        else:
            coord_filter = lambda coords: True
        matrix = SparseMatrix.create_from_coords(simple_text_file_generator(args.input_file,
                                         coord_filter,
                                         coord_transformer = lambda coords : coords_to_hack_map_proj(coords, 
                                                           args.origin_lon, 
                                                           args.origin_lat,
                                                           args.bcube[2])),
                                       args.resolution, {'min': minbcube, 
                                                         'max': maxbcube})   
    
        if args.verbose:
            num_of_cells = 0
            num_of_points = 0
            num_of_cells_with_points = {}
            for cell in matrix.values:
                current_cell_num_points = matrix.values[cell] 
                num_of_cells += 1
                num_of_points += current_cell_num_points 
                if current_cell_num_points in num_of_cells_with_points: 
                    num_of_cells_with_points[current_cell_num_points] += 1
                else:
                    num_of_cells_with_points[current_cell_num_points] = 1
                    
            print("Number of points:", num_of_points)
            print("Number of occupied cells:", num_of_cells)
            print("Average number of points per cell:", num_of_points/num_of_cells)                        
        
        clusters, cluster_list = cluster_matrix_from_cell_matrix(matrix)
        
        if args.verbose:
            print("Number of clusters of contiguous cells:", len(cluster_list))
            big_enough_clusters = 0
            for cluster in cluster_list:
                ncells_in_cluster = len(cluster) 
                if ncells_in_cluster > args.min_cluster_size:
                    big_enough_clusters += 1
            print("Number of clusters with more than min-cluster-size cells:", 
              big_enough_clusters)
        
        if args.output_format == "pov":        
            cells_to_POV(cluster_list, matrix, args.output_file, args.tolerance, 
                         args.min_cluster_size, args.cell_type, args.point_size,
                         args.meld_boxes)
        elif args.output_format == "threejs":
            cells_to_Threejs(cluster_list, matrix, args.output_file, args.tolerance, 
                             args.min_cluster_size, args.cell_type, args.point_size, 
                             args.meld_boxes)
    else: # We are producing an object per each point
        if args.output_format == "pov":
            points_to_POV(simple_text_file_generator(args.input_file,
                        lambda coords : coords_to_hack_map_proj(coords, 
                                          args.origin_lon, 
                                          args.origin_lat,
                                          args.bcube[2])),
                          args.output_file, args.point_size, args.cell_type)
        else:
            print("Options are not compatible with", args.output_format,"output format.")
    if args.verbose:
        print("Processing time: {:.2f} seconds.".format(time.time()-init_time))

    
#################################################################
#################################################################
#################################################################
# Unit Tests


        
        
        
        
        
        

# Allow use both as module and script
if __name__ == "__main__": # script
    main()
else:    
    pass
    # Module specific initialization
