import unittest

from sysmon import cli, collectors


class ParserTests(unittest.TestCase):
    def test_parse_meminfo(self):
        info = collectors.parse_meminfo("MemTotal:  1000 kB\nMemAvailable:   400 kB\n")
        self.assertEqual(info["MemTotal"], 1000 * 1024)
        self.assertEqual(info["MemAvailable"], 400 * 1024)

    def test_parse_cpu_times(self):
        idle, total = collectors.parse_cpu_times("cpu  10 0 10 70 10 0 0 0 0 0\n")
        self.assertEqual(idle, 80)  # idle + iowait
        self.assertEqual(total, 100)


class FormatTests(unittest.TestCase):
    def test_human_bytes(self):
        self.assertEqual(cli.human_bytes(512), "512 B")
        self.assertEqual(cli.human_bytes(2048), "2.0 KiB")

    def test_human_duration(self):
        self.assertEqual(cli.human_duration(90061), "1d 1h 1m")
        self.assertEqual(cli.human_duration(3700), "1h 1m")

    def test_bar(self):
        self.assertTrue(cli.bar(50).startswith("[##########----------]"))


class LiveTests(unittest.TestCase):
    def test_snapshot_renders(self):
        out = cli.render(cli.snapshot(3, 0.1))
        self.assertIn("CPU", out)
        self.assertIn("Memory", out)


if __name__ == "__main__":
    unittest.main()
