import unittest
import tempfile
import os
from pathlib import Path
from harangued import Haranguer


class TestHaranguer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.txt"
        self.h = Haranguer(self.config_path)

    def tearDown(self):
        if self.config_path.exists():
            self.config_path.unlink()
        os.rmdir(self.temp_dir)

    def test_adds_block_to_empty_file(self):
        content = "some initial content\n"
        self.config_path.write_text(content)

        expected = (
            "some initial content\n"
            f"{self.h.start_line}\n"
            "new managed content\n"
            f"{self.h.end_line}\n"
        )

        with self.h as cfg:
            cfg.data.append("new managed content")

        self.assertEqual(self.config_path.read_text(), expected)

    def test_no_duplicate_blocks(self):
        initial = (
            f"{self.h.start_line}\n"
            "existing content\n"
            f"{self.h.end_line}\n"
        )
        self.config_path.write_text(initial)
        expected = (
            f"{self.h.start_line}\n"
            "new content\n"
            f"{self.h.end_line}\n"
        )
        with self.h as cfg:
            cfg.data = ["new content"]
        self.assertEqual(self.config_path.read_text(), expected)

    def test_add_lines_to_block(self):
        initial = (
            f"{self.h.start_line}\n"
            "line1\n"
            f"{self.h.end_line}\n"
        )
        self.config_path.write_text(initial)
        expected = (
            f"{self.h.start_line}\n"
            "line1\nline2\nline3\n"
            f"{self.h.end_line}\n"
        )
        with self.h as cfg:
            cfg.data.extend(["line2", "line3"])
        self.assertEqual(self.config_path.read_text(), expected)

    def test_remove_lines_from_block(self):
        initial = (
            f"{self.h.start_line}\n"
            "line1\nline2\nline3\n"
            f"{self.h.end_line}\n"
        )
        self.config_path.write_text(initial)
        expected = (
            f"{self.h.start_line}\n"
            "line1\n"
            f"{self.h.end_line}\n"
        )
        with self.h as cfg:
            cfg.data = ["line1"]
        self.assertEqual(self.config_path.read_text(), expected)

    def test_preserves_header(self):
        initial = (
            "header line 1\n"
            "header line 2\n"
            f"{self.h.start_line}\n"
            "content\n"
            f"{self.h.end_line}\n"
        )
        self.config_path.write_text(initial)
        expected = (
            "header line 1\n"
            "header line 2\n"
            f"{self.h.start_line}\n"
            "new content\n"
            f"{self.h.end_line}\n"
        )
        with self.h as cfg:
            cfg.data = ["new content"]
        self.assertEqual(self.config_path.read_text(), expected)

    def test_preserves_footer(self):
        initial = (
            f"{self.h.start_line}\n"
            "content\n"
            f"{self.h.end_line}\n"
            "footer line 1\n"
            "footer line 2\n"
        )
        self.config_path.write_text(initial)
        expected = (
            f"{self.h.start_line}\n"
            "new content\n"
            f"{self.h.end_line}\n"
            "footer line 1\n"
            "footer line 2\n"
        )
        with self.h as cfg:
            cfg.data = ["new content"]
        self.assertEqual(self.config_path.read_text(), expected)
