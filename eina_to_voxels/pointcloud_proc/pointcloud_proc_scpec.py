import unittest
import pointcloud_proc


class TestPointCloudProc(unittest.TestCase):
    def setUp(self):
        self.origin_lon = -0.89047
        self.origin_lat = 41.6661
        self.bcube = {'min': (15.5, 12.1, -3.2),
                      'max': (18.9, 13.2, 8.4)}

    def testHackMapProjection(self):
        x, y = pointcloud_proc.hack_map_projection(-0.893141, 41.667879,
                                   self.origin_lon, self.origin_lat)
        self.assertAlmostEqual(x, -198.22290660588757)
        self.assertAlmostEqual(y, 198.03737415306065)

    def testCalculateCellSize(self):
        resolution = (10, 10, 16)
        size = pointcloud_proc.calculate_cell_size(resolution, self.bcube)
        self.assertAlmostEqual(size[0], 0.34)
        self.assertAlmostEqual(size[1], 0.11)
        self.assertAlmostEqual(size[2], 0.725)

    def testCoordsToHackMapProj(self):
        coords = (-0.893141, 41.667879, 25.2)
        result = pointcloud_proc.coords_to_hack_map_proj(coords, self.origin_lon, self.origin_lat, 12.1)
        self.assertAlmostEqual(result[0], -198.22290660588757)
        self.assertAlmostEqual(result[1], 198.03737415306065)
        self.assertAlmostEqual(result[2], 13.1)

    def testCoordsToCellMatrix(self):
        coords = ((15.5, 12.1, -3.2),  # 0,0,0
                  (15.51, 12.11, -3.19),  # 0,0,0
                  (18.89, 12.11, -3.19),  # 2,0,0
                  (18.9, 12.11, -3.10),  # 2,0,0
                  (18.89, 12.4, -3.19),  # 2,1,0
                  (18.89, 12.4, 8.2))  # 2,1,1
        resolution = (3, 4, 2)
        matrix = pointcloud_proc.SparseMatrix.create_from_coords(coords, resolution, self.bcube)
        self.assertTupleEqual(resolution, matrix.resolution)
        self.assertTupleEqual(self.bcube['min'], matrix.bcube['min'])
        self.assertTupleEqual(self.bcube['max'], matrix.bcube['max'])
        self.assertIn((0, 0, 0), matrix.values)
        self.assertIn((2, 0, 0), matrix.values)
        self.assertIn((2, 1, 0), matrix.values)
        self.assertIn((2, 1, 1), matrix.values)
        self.assertEqual(matrix.values[(0, 0, 0)], 2)
        self.assertEqual(matrix.values[(2, 0, 0)], 2)
        self.assertEqual(matrix.values[(2, 1, 0)], 1)
        self.assertEqual(matrix.values[(2, 1, 1)], 1)
        self.assertNotIn((1, 1, 1), matrix.values)
        self.assertNotIn((0, 1, 1), matrix.values)
        self.assertNotIn((0, 0, 1), matrix.values)
        self.assertNotIn((2, 2, 2), matrix.values)
        self.assertNotIn((2, 2, 0), matrix.values)
        self.assertNotIn((2, 0, 2), matrix.values)

    def testCellToCoords(self):
        cells = [(0, 0, 0), (1, 0, 0), (1, 5, 3)]
        resolution = (2, 6, 4)
        bcube = {'min': (0, 0, 0),
                 'max': (1, 3, 1)}
        coords = [(0, 0, 0, 0.5, 0.5, 0.25),
                  (0.5, 0, 0, 1, 0.5, 0.25),
                  (0.5, 2.5, 0.75, 1, 3.0, 1)]
        for i in range(len(cells)):
            self.assertTupleEqual(pointcloud_proc.cell_to_coords(cells[i], resolution, bcube),
                                  coords[i])

    def testAreFullBox(self):
        cells = [(0, 0, 0)]
        min_cell = (0, 0, 0)
        max_cell = (0, 0, 0)
        self.assertTrue(pointcloud_proc.are_full_box(cells, min_cell, max_cell))
        self.assertFalse(pointcloud_proc.are_full_box(cells, min_cell, (0, 0, 1)))

        cells = [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0)]
        self.assertTrue(pointcloud_proc.are_full_box(cells, min_cell, (1, 1, 0)))

    def testAreEmptyBox(self):
        cells = [(0, 0, 0)]
        min_cell = (0, 0, 0)
        max_cell = (0, 0, 0)
        self.assertFalse(pointcloud_proc.are_empty_box(cells, min_cell, max_cell))
        self.assertFalse(pointcloud_proc.are_empty_box(cells, min_cell, (0, 0, 1)))

        cells = [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0)]
        self.assertTrue(pointcloud_proc.are_empty_box(cells, (2, 2, 2), (3, 3, 3)))

    def testCellsToBoxes(self):
        cells = [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0),
                 (0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 1)]
        self.assertEqual([(0, 0, 0, 1, 1, 1)], pointcloud_proc.cells_to_boxes(cells, (0, 0, 0), (3, 3, 3)))
        cells.append((3, 3, 3))
        self.assertEqual([(0, 0, 0, 1, 1, 1), (3, 3, 3, 3, 3, 3)],
                         pointcloud_proc.cells_to_boxes(cells, (0, 0, 0), (3, 3, 3)))

    def testMinMaxCells(self):
        cells = [(0, 1, 2), (0, 2, 1), (1, 3, 4), (1, 4, 4)]
        self.assertEqual((0, 1, 1, 1, 4, 4), pointcloud_proc.min_max_cells(cells))
        cells = [(0, 1, 2), (1, 2, 0), (2, 3, 4), (1, 5, 8)]
        self.assertEqual((0, 1, 0, 2, 5, 8), pointcloud_proc.min_max_cells(cells))

if __name__ == '__main__':
    unittest.main()