import unittest
import debug.display
import tracemalloc


class TestSnapshot(unittest.TestCase):
    def test_(self):
        tracemalloc.start(30)
        snapshot = tracemalloc.take_snapshot()
        debug.display.snapshot_top(snapshot)
