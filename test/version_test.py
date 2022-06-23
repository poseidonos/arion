from packaging import version

import unittest


class TestVersion(unittest.TestCase):
    def test_fio_version(self):
        v1 = "fio-3.1-dirty"
        v27 = "fio-3.27-64-ga006-dirty"
        v28 = "fio-3.28"
        v1 = v1[4:].split("-")[0]
        v27 = v27[4:].split("-")[0]
        v28 = v28[4:].split("-")[0]
        self.assertEqual(v1, "3.1")
        self.assertEqual(v27, "3.27")
        self.assertEqual(v28, "3.28")
        self.assertEqual(version.parse(v1) < version.parse(v27), True)
        self.assertEqual(version.parse(v1) < version.parse(v28), True)
        self.assertEqual(version.parse(v27) < version.parse(v28), True)
        self.assertEqual(version.parse(v1) >= version.parse("3.3"), False)
