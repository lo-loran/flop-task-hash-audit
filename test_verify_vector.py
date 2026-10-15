import json, subprocess, sys, tempfile, unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "verify_vector.py"
FIXTURE = Path(__import__("os").environ.get("FLOP_VECTOR_FIXTURE", HERE / "wire-format-v1.json"))
class VectorTests(unittest.TestCase):
    def run_doc(self, doc):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "fixture.json"
            p.write_text(json.dumps(doc), encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPT), str(p)], capture_output=True, text=True)
    def fixture(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))
    def test_official_vector_passes(self):
        r = self.run_doc(self.fixture())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
    def assert_failure(self, doc, expected):
        r = self.run_doc(doc)
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr, r.stderr)
        for message in expected:
            self.assertIn("FAIL | " + message, r.stdout, r.stdout + r.stderr)

    def test_each_task_hash_input_mutation_fails(self):
        original = self.fixture()
        fields = ("genesis_hash_hex", "agent_account_id32_hex", "nonce", "model_hash_hex", "payload_hash_hex", "commit_hash_hex")
        for field in fields:
            with self.subTest(field=field):
                d = json.loads(json.dumps(original))
                inputs = d["direct_rail_v1"]["task_hash"]["inputs"]
                if field == "nonce":
                    inputs[field] = str(int(inputs[field]) + 1)
                else:
                    raw = bytearray.fromhex(inputs[field])
                    raw[0] ^= 1
                    inputs[field] = raw.hex()
                self.assert_failure(d, ("task preimage", "task hash"))

    def test_modified_output_hash_fails(self):
        d = self.fixture()
        d["direct_rail_v1"]["inputs"]["output_hash_hex"] = "ff" * 32
        self.assert_failure(d, ("report preimage", "report data"))

    def test_modified_report_data_fails(self):
        d = self.fixture()
        d["direct_rail_v1"]["report_data_hex"] = "00" * 64
        self.assert_failure(d, ("report data",))

    def test_modified_task_preimage_fails(self):
        d = self.fixture()
        p = d["direct_rail_v1"]["task_hash"]["preimage_hex"]
        d["direct_rail_v1"]["task_hash"]["preimage_hex"] = "00" * (len(p) // 2)
        self.assert_failure(d, ("task preimage",))

    def assert_invalid_text(self, source):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "fixture.json"
            p.write_text(source, encoding="utf-8")
            r = subprocess.run([sys.executable, str(SCRIPT), str(p)], capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("ERROR |", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_invalid_json_is_reported_cleanly(self):
        self.assert_invalid_text("{")

    def test_missing_section_is_reported_cleanly(self):
        self.assert_invalid_text("{}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
