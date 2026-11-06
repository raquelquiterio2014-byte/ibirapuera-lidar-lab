import unittest
import numpy as np
from audit import mask_roi, ROI
class Boundaries(unittest.TestCase):
    def test_half_open_boundary(self):
        a,b,c,d=ROI
        actual=mask_roi(np.array([a,c,a,a+1]),np.array([b,b,d,b+1]))
        self.assertEqual(actual.tolist(),[True,False,False,True])
if __name__=='__main__': unittest.main()
