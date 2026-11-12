import unittest

from logsift import cli

ACCESS = [
    '1.1.1.1 - - [10/Oct/2025:13:55:36 +0000] "GET /a HTTP/1.1" 200 10\n',
    '1.1.1.1 - - [10/Oct/2025:13:55:37 +0000] "GET /a HTTP/1.1" 404 10\n',
    '2.2.2.2 - - [10/Oct/2025:13:55:38 +0000] "POST /b HTTP/1.1" 200 10\n',
]
SYSLOG = [
    "Nov 11 12:00:01 host sshd[123]: Failed password for root from 9.9.9.9 port 22 ssh2\n",
    "Nov 11 12:00:02 host sshd[123]: Failed password for invalid user bob from 9.9.9.9 port 22 ssh2\n",
    "Nov 11 12:00:03 host kernel: ERROR something broke\n",
]


class AnalyzeTests(unittest.TestCase):
    def test_access_log(self):
        s = cli.analyze(ACCESS)
        self.assertEqual(s["total"], 3)
        self.assertEqual(s["status"]["200"], 2)
        self.assertEqual(s["ips"].most_common(1), [("1.1.1.1", 2)])
        self.assertEqual(s["paths"]["/a"], 2)

    def test_syslog(self):
        s = cli.analyze(SYSLOG)
        self.assertEqual(s["failed_logins"]["9.9.9.9"], 2)
        self.assertEqual(s["levels"]["ERROR"], 1)
        self.assertEqual(s["processes"]["sshd"], 2)

    def test_unparsed_and_blank(self):
        s = cli.analyze(["\n", "garbage line\n"])
        self.assertEqual(s["total"], 1)
        self.assertEqual(s["unparsed"], 1)

    def test_render_mentions_sections(self):
        out = cli.render(cli.analyze(ACCESS + SYSLOG))
        self.assertIn("HTTP status codes", out)
        self.assertIn("Failed SSH logins", out)


if __name__ == "__main__":
    unittest.main()
