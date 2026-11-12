import unittest

from pkgx import cli


class DetectTests(unittest.TestCase):
    def test_direct_id(self):
        self.assertEqual(cli.detect_manager({"ID": "fedora"}), "dnf")

    def test_id_like(self):
        self.assertEqual(cli.detect_manager({"ID": "pop", "ID_LIKE": "ubuntu debian"}), "apt")

    def test_parse_os_release(self):
        d = cli.parse_os_release('ID=arch\nNAME="Arch Linux"\n# comment\n')
        self.assertEqual(d["ID"], "arch")
        self.assertEqual(d["NAME"], "Arch Linux")


class CommandTests(unittest.TestCase):
    def test_install_uses_sudo_when_not_root(self):
        self.assertEqual(cli.build_command("apt", "install", ["vim"], False), ["sudo", "apt", "install", "vim"])

    def test_no_sudo_as_root(self):
        self.assertEqual(cli.build_command("dnf", "install", ["vim"], True), ["dnf", "install", "vim"])

    def test_search_never_needs_root(self):
        self.assertEqual(cli.build_command("pacman", "search", ["vim"], False), ["pacman", "-Ss", "vim"])

    def test_yes_flag(self):
        self.assertEqual(cli.build_command("pacman", "install", ["vim"], True, True), ["pacman", "-S", "--noconfirm", "vim"])
        self.assertEqual(cli.build_command("apt", "install", ["vim"], True, True), ["apt", "install", "-y", "vim"])


if __name__ == "__main__":
    unittest.main()
