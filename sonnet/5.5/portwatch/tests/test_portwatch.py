import unittest

from portwatch import core

SAMPLE = """  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
   0: 0100007F:0050 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 11111 1 0 100 0 0 10 0
   1: 00000000:1F90 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 22222 1 0 100 0 0 10 0
   2: 0100007F:9C40 0100007F:0050 01 00000000:00000000 00:00000000 00000000     0        0 33333 1 0 100 0 0 10 0
"""


class DecodeTests(unittest.TestCase):
    def test_ipv4(self):
        self.assertEqual(core.decode_addr("0100007F:0050"), ("127.0.0.1", 80))
        self.assertEqual(core.decode_addr("00000000:1F90"), ("0.0.0.0", 8080))

    def test_ipv6_loopback(self):
        self.assertEqual(core.decode_addr("00000000000000000000000001000000:0016"), ("::1", 22))

    def test_ipv6_any(self):
        self.assertEqual(core.decode_addr("00000000000000000000000000000000:0050"), ("::", 80))


class ScopeTests(unittest.TestCase):
    def test_scope(self):
        self.assertEqual(core.scope("127.0.0.53"), "localhost only")
        self.assertEqual(core.scope("::1"), "localhost only")
        self.assertEqual(core.scope("0.0.0.0"), "all interfaces")
        self.assertEqual(core.scope("::"), "all interfaces")
        self.assertEqual(core.scope("172.17.0.1"), "single interface")


class ParseTests(unittest.TestCase):
    def test_only_listening(self):
        socks = core.parse_proc_net(SAMPLE)
        self.assertEqual([(s["ip"], s["port"]) for s in socks], [("127.0.0.1", 80), ("0.0.0.0", 8080)])
        self.assertEqual(socks[0]["inode"], "11111")


class LiveTests(unittest.TestCase):
    def test_listening_runs(self):
        for s in core.listening():
            self.assertIn("exposed", s)


if __name__ == "__main__":
    unittest.main()
