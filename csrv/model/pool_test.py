import unittest
from csrv.model import events
from csrv.model import pool


class TestPool(unittest.TestCase):

  def setUp(self):
    self.pool = pool.Pool(None, None, 5)

  def testPoolValue(self):
    self.assertEqual(5, self.pool.value)

  def testGain(self):
    self.pool.gain(7)
    self.assertEqual(12, self.pool.value)

  def testLose(self):
    self.pool.lose(3)
    self.assertEqual(2, self.pool.value)

  def testReset(self):
    self.pool.lose(2)
    self.pool.reset()
    self.assertEqual(5, self.pool.value)


if __name__ == '__main__':
  unittest.main()
