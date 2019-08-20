import sys
sys.path.append('../openaudit')
import controller_collector
import unittest


class IsolationCollectorTest(unittest.TestCase):

    c = controller_collector.IsolationControllerCollector()

    def testController(self):
        snapshot_id = 1
        data = self.c.getData()
        size = len(data)
        self.assertEqual(self.c.saveData(data, snapshot_id), size, "Should be "+str(size))

    def testCompute(self):
        pass


if __name__ == '__main__':
    unittest.main()