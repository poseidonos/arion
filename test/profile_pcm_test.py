import profile.pcm
import unittest


class TestPCM(unittest.TestCase):
    def test_draw_pcm_memory_graph(self):
        profile.pcm.draw_pcm_memory_graph(
            "./test/profile_pcm_memory_test.csv",
            "./result_mem.png"
        )

    def test_draw_pcm_cpu_graph(self):
        profile.pcm.draw_pcm_cpu_graph(
            "./test/profile_pcm_cpu_test.csv",
            "./result_cpu.png"
        )
