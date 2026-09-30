"""
Unit tests for bulk_converter.py (Direct Excel/CSV/ZIP to JSON/JSONL streaming).
"""

import os
import json
import zipfile
import tempfile
import unittest
import pandas as pd

from src.us_b2b.utils.bulk_converter import (
    stream_csv_to_jsonl,
    stream_excel_to_jsonl,
    zip_to_jsonl,
    jsonl_to_json_records,
)


class TestBulkConverter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sample_data = [
            {"company_name": "Acme Corp", "ein": "12-3456789", "executive": "Jane Doe", "title": "CEO"},
            {"company_name": "Beta LLC", "ein": "98-7654321", "executive": "John Smith", "title": "CFO"},
        ]

    def test_stream_csv_to_jsonl(self):
        csv_path = os.path.join(self.temp_dir, "test.csv")
        jsonl_path = os.path.join(self.temp_dir, "output_csv.jsonl")

        # Create sample CSV
        df = pd.DataFrame(self.sample_data)
        df.to_csv(csv_path, index=False)

        # Convert to JSONL
        count = stream_csv_to_jsonl(csv_path, jsonl_path, chunk_size=10)
        self.assertEqual(count, 2)

        records = jsonl_to_json_records(jsonl_path)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["company_name"], "Acme Corp")
        self.assertEqual(records[1]["executive"], "John Smith")

    def test_stream_excel_to_jsonl(self):
        excel_path = os.path.join(self.temp_dir, "test.xlsx")
        jsonl_path = os.path.join(self.temp_dir, "output_excel.jsonl")

        # Create sample Excel
        df = pd.DataFrame(self.sample_data)
        df.to_excel(excel_path, index=False)

        # Convert to JSONL
        count = stream_excel_to_jsonl(excel_path, jsonl_path)
        self.assertEqual(count, 2)

        records = jsonl_to_json_records(jsonl_path)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["title"], "CEO")

    def test_zip_to_jsonl(self):
        csv_path = os.path.join(self.temp_dir, "test_inner.csv")
        zip_path = os.path.join(self.temp_dir, "test.zip")
        jsonl_path = os.path.join(self.temp_dir, "output_zip.jsonl")

        # Create sample CSV & ZIP
        df = pd.DataFrame(self.sample_data)
        df.to_csv(csv_path, index=False)

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.write(csv_path, arcname="awards.csv")

        # Convert ZIP to JSONL directly
        count = zip_to_jsonl(zip_path, jsonl_path, target_extension=".csv")
        self.assertEqual(count, 2)

        records = jsonl_to_json_records(jsonl_path)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["company_name"], "Acme Corp")


if __name__ == "__main__":
    unittest.main()
