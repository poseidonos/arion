import lib
import unittest


class TestSubproc(unittest.TestCase):
    def test_sync_run(self):
        result = lib.sync_run("uname")
        self.assertEqual(result, "Linux\n")

    def test_sync_parallel_run(self):
        results = lib.sync_parallel_run(["uname", "uname"])
        self.assertEqual(results[0], "Linux\n")
        self.assertEqual(results[1], "Linux\n")

    def test_async_run(self):
        count = 1
        thread = lib.async_run("sleep 1")
        count += 1
        self.assertEqual(count, 2)
        # result = thread.join()
        # print(result)

    def test_async_paraller_run(self):
        count = 1
        threads = lib.async_parallel_run(["sleep 1", "sleep 1"])
        count += 2
        self.assertEqual(count, 3)
        # results = [thread.join() for thread in threads]
        # print(results)
