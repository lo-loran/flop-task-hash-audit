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
    def test_modified_nonce_fails(self):
        d = self.fixture()
        i = d["direct_rail_v1"]["task_hash"]["inputs"]
        i["nonce"] = str(int(i["nonce"]) + 1)
        self.assertNotEqual(self.run_doc(d).returncode, 0)
    def test_modified_output_hash_fails(self):
        d = self.fixture()
        d["direct_rail_v1"]["inputs"]["output_hash_hex"] = "ff" * 32
        self.assertNotEqual(self.run_doc(d).returncode, 0)
    def test_modified_report_data_fails(self):
        d = self.fixture()
        d["direct_rail_v1"]["report_data_hex"] = "00" * 64
        self.assertNotEqual(self.run_doc(d).returncode, 0)
    def test_modified_task_preimage_fails(self):
        d = self.fixture()
        p = d["direct_rail_v1"]["task_hash"]["preimage_hex"]
        d["direct_rail_v1"]["task_hash"]["preimage_hex"] = "00" * (len(p) // 2)
        self.assertNotEqual(self.run_doc(d).returncode, 0)
if __name__ == "__main__":
    unittest.main(verbosity=2)
