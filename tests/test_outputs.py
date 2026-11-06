import json
import unittest
import numpy as np
from audit import ROOT, ROI
class RealDataOutputs(unittest.TestCase):
    def test_counts_and_preview(self):
        r=json.loads((ROOT/'outputs/audit.json').read_text())
        with np.load(ROOT/'outputs/preview.npz') as d:
            self.assertEqual(sum(r['tile_classes'].values()),r['header']['point_count'])
            self.assertEqual(sum(r['roi_classes'].values()),int(d['coverage'].sum()))
            self.assertEqual(r['roi_classes']['2'],int(d['ground'].sum()))
            p=d['points']
            self.assertLessEqual(len(p),100000)
            self.assertTrue(np.all((p[:,0]>=ROI[0])&(p[:,0]<ROI[2])))
            self.assertTrue(np.all((p[:,1]>=ROI[1])&(p[:,1]<ROI[3])))
