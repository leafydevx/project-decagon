import os
import tempfile
import unittest

from secaudit import checks


class SshdTests(unittest.TestCase):
    def test_first_directive_wins(self):
        cfg = checks.parse_sshd_config("PermitRootLogin no\nPermitRootLogin yes\n# x\n")
        self.assertEqual(cfg["permitrootlogin"], "no")

    def test_root_login_yes_fails(self):
        r = checks.check_sshd("PermitRootLogin yes\nPasswordAuthentication no\n")
        self.assertEqual(r[0][0], checks.FAIL)
        self.assertEqual(r[1][0], checks.PASS)

    def test_defaults_warn_on_password_auth(self):
        r = checks.check_sshd("")
        self.assertEqual(r[0][0], checks.PASS)
        self.assertEqual(r[1][0], checks.WARN)


class PasswdTests(unittest.TestCase):
    def test_extra_uid0(self):
        r = checks.check_passwd("root:x:0:0::/root:/bin/sh\ntoor:x:0:0::/:/bin/sh\n")
        self.assertEqual(r[0][0], checks.FAIL)
        self.assertIn("toor", r[0][1])

    def test_clean(self):
        self.assertEqual(checks.check_passwd("root:x:0:0::/root:/bin/sh\nbob:x:1000:1000::/h:/bin/sh\n")[0][0], checks.PASS)


class ModeTests(unittest.TestCase):
    def test_modes(self):
        with tempfile.NamedTemporaryFile() as f:
            os.chmod(f.name, 0o600)
            self.assertEqual(checks.check_mode(f.name, 0o640)[0][0], checks.PASS)
            os.chmod(f.name, 0o666)
            self.assertEqual(checks.check_mode(f.name, 0o640)[0][0], checks.FAIL)

    def test_missing_file_is_not_a_failure(self):
        self.assertEqual(checks.check_mode("/nonexistent/zzz", 0o600)[0][0], checks.PASS)


if __name__ == "__main__":
    unittest.main()
