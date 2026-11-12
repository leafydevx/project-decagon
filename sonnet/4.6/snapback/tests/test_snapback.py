"""Unit tests for snapback (no root required, no real rsync calls)."""

import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call


class TestListBackups(unittest.TestCase):
    def test_empty_dir(self):
        from snapback.backup import list_backups
        with tempfile.TemporaryDirectory() as d:
            result = list_backups(d)
            self.assertEqual(result, [])

    def test_sorted_newest_first(self):
        from snapback.backup import list_backups
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            names = ["20240101_120000", "20240103_090000", "20240102_080000"]
            for n in names:
                (root / n).mkdir()
            result = list_backups(d)
            self.assertEqual([r.name for r in result],
                             ["20240103_090000", "20240102_080000", "20240101_120000"])

    def test_nonexistent_root(self):
        from snapback.backup import list_backups
        result = list_backups("/tmp/snapback_no_such_dir_xyz")
        self.assertEqual(result, [])


class TestLatestBackup(unittest.TestCase):
    def test_picks_latest(self):
        from snapback.backup import _latest_backup
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "20240101_000000").mkdir()
            (root / "20240105_000000").mkdir()
            latest = _latest_backup(root)
            self.assertEqual(latest.name, "20240105_000000")

    def test_excludes_current(self):
        from snapback.backup import _latest_backup
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "20240101_000000").mkdir()
            (root / "20240105_000000").mkdir()
            latest = _latest_backup(root, exclude="20240105_000000")
            self.assertEqual(latest.name, "20240101_000000")

    def test_none_when_empty(self):
        from snapback.backup import _latest_backup
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(_latest_backup(d))


class TestRunBackup(unittest.TestCase):
    @patch("snapback.backup.subprocess.run")
    @patch("snapback.backup._rsync_available", return_value=True)
    def test_incremental_link_dest(self, _avail, mock_run):
        from snapback.backup import run_backup
        mock_run.return_value = MagicMock(returncode=0)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # pre-existing backup for link-dest
            (root / "20240101_000000").mkdir()

            with tempfile.TemporaryDirectory() as src:
                run_backup([src], str(root), incremental=True)

        cmd = mock_run.call_args[0][0]
        self.assertIn("--link-dest", cmd)

    @patch("snapback.backup.subprocess.run")
    @patch("snapback.backup._rsync_available", return_value=True)
    def test_full_no_link_dest(self, _avail, mock_run):
        from snapback.backup import run_backup
        mock_run.return_value = MagicMock(returncode=0)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "20240101_000000").mkdir()
            with tempfile.TemporaryDirectory() as src:
                run_backup([src], str(root), incremental=False)

        cmd = mock_run.call_args[0][0]
        self.assertNotIn("--link-dest", cmd)

    @patch("snapback.backup._rsync_available", return_value=False)
    def test_no_rsync_raises(self, _avail):
        from snapback.backup import run_backup
        with self.assertRaises(RuntimeError):
            run_backup(["/tmp"], "/tmp/out")

    @patch("snapback.backup.subprocess.run")
    @patch("snapback.backup._rsync_available", return_value=True)
    def test_dry_run_flag(self, _avail, mock_run):
        from snapback.backup import run_backup
        mock_run.return_value = MagicMock(returncode=0)
        with tempfile.TemporaryDirectory() as d:
            with tempfile.TemporaryDirectory() as src:
                run_backup([src], d, dry_run=True)
        cmd = mock_run.call_args[0][0]
        self.assertIn("--dry-run", cmd)

    @patch("snapback.backup.subprocess.run")
    @patch("snapback.backup._rsync_available", return_value=True)
    def test_exclude_passed(self, _avail, mock_run):
        from snapback.backup import run_backup
        mock_run.return_value = MagicMock(returncode=0)
        with tempfile.TemporaryDirectory() as d:
            with tempfile.TemporaryDirectory() as src:
                run_backup([src], d, exclude=["*.log", "tmp/"])
        cmd = mock_run.call_args[0][0]
        self.assertIn("*.log", cmd)
        self.assertIn("tmp/", cmd)


class TestPartitionToDisk(unittest.TestCase):
    def test_sda1(self):
        from snapback.bootable import _partition_to_disk
        self.assertEqual(_partition_to_disk("/dev/sda1"), "/dev/sda")

    def test_nvme(self):
        from snapback.bootable import _partition_to_disk
        self.assertEqual(_partition_to_disk("/dev/nvme0n1p2"), "/dev/nvme0n1")

    def test_no_partition(self):
        from snapback.bootable import _partition_to_disk
        self.assertEqual(_partition_to_disk("/dev/sdb"), "/dev/sdb")


class TestPatchFstab(unittest.TestCase):
    def test_replaces_root_uuid(self):
        from snapback.bootable import _patch_fstab
        content = (
            "# /etc/fstab\n"
            "UUID=old-uuid-1234  /       ext4  defaults  0 1\n"
            "UUID=boot-uuid-5678 /boot   vfat  umask=0077 0 2\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix="fstab", delete=False) as f:
            f.write(content)
            fpath = Path(f.name)
        try:
            _patch_fstab(fpath, "new-uuid-abcd")
            result = fpath.read_text()
            self.assertIn("UUID=new-uuid-abcd", result)
            self.assertIn("UUID=boot-uuid-5678", result)  # /boot unchanged
        finally:
            fpath.unlink()


class TestRestoreBackup(unittest.TestCase):
    def test_missing_backup_raises(self):
        from snapback.restore import restore_backup
        with self.assertRaises(FileNotFoundError):
            restore_backup("/tmp/snapback_nonexistent_xyz", "/tmp/out")

    @patch("snapback.restore.subprocess.run")
    @patch("snapback.restore.shutil.which", return_value="/usr/bin/rsync")
    def test_restore_calls_rsync(self, _which, mock_run):
        from snapback.restore import restore_backup
        mock_run.return_value = MagicMock(returncode=0)
        with tempfile.TemporaryDirectory() as src:
            with tempfile.TemporaryDirectory() as dst:
                restore_backup(src, dst)
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], "rsync")


if __name__ == "__main__":
    unittest.main()
