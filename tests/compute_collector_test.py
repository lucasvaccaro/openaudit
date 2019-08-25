import sys
sys.path.append('../openaudit')
import compute_collector
import unittest


class IsolationComputeCollectorTest(unittest.TestCase):

    c = compute_collector.IsolationComputeCollector()

    def test(self):
        snapshot_id = 1
        host = "ubuntusrv"
        vms = "wiqeue289e19\nweiqoje329\neje28ej1ei"
        data = self.c.parseData((host, vms))
        res = self.c.saveData(data, snapshot_id)
        size = 3
        msg = "Result: " + str(res) + " Should be " + str(size)
        self.assertEqual(res, size, msg)


if __name__ == '__main__':
    unittest.main()