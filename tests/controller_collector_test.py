import sys
sys.path.append('../openaudit')
import controller_collector
import unittest


class IsolationControllerCollectorTest(unittest.TestCase):

    c = controller_collector.IsolationControllerCollector()

    def test(self):
        snapshot_id = 1
        data = self.c.getData()
        size = len(data)
        self.assertEqual(self.c.saveData(data, snapshot_id), size, "Should be "+str(size))


if __name__ == '__main__':
    unittest.main()