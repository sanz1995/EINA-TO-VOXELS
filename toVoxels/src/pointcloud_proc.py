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
        
        colors = [(221,221,221,1),(219,125,62,1.2),(179,80,188,1.2),(107,138,201,1.1),(177,166,39,1),(65,174,56,1),(208,132,153,1.1),(64,64,64,1),(154,161,161,1),(46,110,137,1),(126,61,181,1.1),(46,56,141,1),(79,50,31,1),(53,70,27,1),(150,52,48,1.1),(25,22,22,1)]

        scores = [];
        matrix = SparseMatrix({}, resolution, bcube)     
        for coords in coords_iterator:
            ncell = coords_to_cell(coords, resolution, bcube)
            if ncell in matrix.values:
                matrix.values[ncell] += (1,0)
                #print(matrix.values[ncell])
                #print(coords)
                #print("-----------")
            else:
                
                for color in colors:
                    scores.append(abs((color[0]-coords[3]/256))+abs((color[1]-coords[4]/256))+abs((color[2]-coords[5]/256)))
                
                min = scores[0]
                best = 0
                for i in range(0, 15):
                    if ((scores[i]*colors[i][3]) < min):
                        min = scores[i]*colors[i][3]
                        best = i;
            
            
                scores=[]
                matrix.values[ncell] = (1,best)
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
    #print(coords)
    x = coords[0]
    y = coords[1]
    z = coords[2]
    minx, miny, minz = bcube['min']
    maxx, maxy, maxz = bcube['max']
    #print(x)
    #print(minx)
    #print("----------")
    assert(x >= minx and x <= maxx)
    assert(y >= miny and y <= maxy)
    assert(z >= minz and z <= maxz)
    
    #print(maxx - minx)
    #print(resolution[0])
                   
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
    #print("---------")
    assert(ncell[0] >= 0 and ncell[0] < resolution[0])
    assert(ncell[1] >= 0 and ncell[1] < resolution[1])
    assert(ncell[2] >= 0 and ncell[2] < resolution[2])
    
    return ncell        


def join(matrix):
    new_matrix = SparseMatrix({}, matrix.resolution, matrix.bcube)
    neighbor = 0
    neighbor_colors = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    
    
    
    resolution = matrix.resolution
    n=0;
    
    for i in range(0,resolution[0]):
        for j in range(0,resolution[1]):
            for k in range(0,resolution[2]):
                if (i,j,k) in matrix.values:
                    new_matrix.values[(i,j,k)] = (1,matrix.values[(i,j,k)][1])
                else:
                    for p in [-1, 1]:
                        if(i+p,j,k) in matrix.values:
                            neighbor_colors[matrix.values[(i+p,j,k)][1]]+=1
                            neighbor+=1
                        if(i,j+p,k) in matrix.values:
                            neighbor_colors[matrix.values[(i,j+p,k)][1]]+=1
                            neighbor+=1
                        if(i+p,j+p,k) in matrix.values:
                            neighbor_colors[matrix.values[(i+p,j+p,k)][1]]+=1
                            neighbor+=1
                            
                        if(i-p,j-p,k) in matrix.values:
                            neighbor_colors[matrix.values[(i-p,j-p,k)][1]]+=1
                            neighbor+=1
                                 
                    if (neighbor > 3):
                        n+=1
                        new_matrix.values[(i,j,k)] = (1,neighbor_colors.index(max(neighbor_colors)))
                    neighbor_colors = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                    neighbor = 0  
    print(n)
    return new_matrix


def deleteIsolated(matrix):
    resolution = matrix.resolution
    for i in range(0,resolution[0]):
        for j in range(0,resolution[1]):
            for k in range(0,resolution[2]):
                if (i,j,k) in matrix.values:
                    if SparseMatrix.neighbor_26(matrix,(i,j,k)) == None:
                        del matrix.values[(i,j,k)]


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
                  
    

