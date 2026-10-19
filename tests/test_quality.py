"""Tests for the CSV quality toolkit."""

import tempfile
import unittest
from pathlib import Path

from dslab.quality import infer_type, profile_csv, write_report


class InferTypeTests(unittest.TestCase):
    def test_integer_values(self):
        self.assertEqual(infer_type(["12", "15"]), "integer")

    def test_decimal_values(self):
        self.assertEqual(infer_type(["12.5", "15.0"]), "number")

    def test_text_values(self):
        self.assertEqual(infer_type(["Ahmedabad", "Rajkot"]), "string")

    def test_empty_values(self):
        self.assertEqual(infer_type([]), "empty")


class ProfileCsvTests(unittest.TestCase):
    def test_detects_missing_and_duplicate_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.csv"
            path.write_text(
                "id,city\n1,Surat\n2,\n2,\n",
                encoding="utf-8",
            )

            report = profile_csv(path)

            self.assertEqual(report["row_count"], 3)
            self.assertEqual(report["column_count"], 2)
            self.assertEqual(report["missing_by_column"]["city"], 2)
            self.assertEqual(report["duplicate_row_count"], 1)
            self.assertEqual(report["quality_status"], "needs_review")

    def test_clean_data_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "clean.csv"
            path.write_text(
                "id,city\n1,Surat\n2,Rajkot\n",
                encoding="utf-8",
            )

            report = profile_csv(path)

            self.assertEqual(report["missing_cell_count"], 0)
            self.assertEqual(report["duplicate_row_count"], 0)
            self.assertEqual(report["quality_status"], "passed")

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            profile_csv("does-not-exist.csv")

    def test_duplicate_headers_raise(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            path.write_text("id,id\n1,2\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                profile_csv(path)

    def test_report_is_written_as_json(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "sample.csv"
            output = Path(folder) / "reports" / "quality.json"
            source.write_text("id\n1\n", encoding="utf-8")

            write_report(profile_csv(source), output)

            self.assertTrue(output.is_file())
            self.assertIn('"row_count": 1', output.read_text())

    def test_extra_fields_raise(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            path.write_text("id\n1,2\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                profile_csv(path)


if __name__ == "__main__":
    unittest.main()
