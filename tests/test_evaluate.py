import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate.py"


def run_record(run_id, variant="baseline", **overrides):
    record = {
        "run_id": run_id, "case_id": "login", "variant": variant, "environment": "fixture-v1",
        "requested_model": "model-requested", "observed_model": None, "model_evidence": None,
        "outcome": "accepted", "checks": [{"name": "works", "passed": True, "evidence": "check://login"}],
        "attempts": 1, "duration_seconds": 2.5, "input_tokens": 100, "cached_input_tokens": 30,
        "output_tokens": 20, "human_interventions": 0, "evidence": ["artifact://login"],
    }
    record.update(overrides)
    return record


class EvaluateTests(unittest.TestCase):
    def report(self, payload):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8") as handle:
            json.dump(payload, handle)
            handle.flush()
            return subprocess.run([sys.executable, str(SCRIPT), "report", "--input", handle.name], text=True, capture_output=True)

    def test_paired_report_counts_failures_and_token_subset(self):
        failed = run_record("base-2", outcome="failed", checks=[], duration_seconds=1, input_tokens=40, cached_input_tokens=10, output_tokens=5)
        candidate = run_record("cand-1", "candidate", duration_seconds=3, input_tokens=90, cached_input_tokens=20, output_tokens=30)
        result = self.report({"schema_version": 1, "runs": [run_record("base-1"), failed, candidate]})
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        baseline = report["cases"][0]["baseline"]
        self.assertEqual(baseline["outcomes"]["failed"], 1)
        self.assertEqual(baseline["metrics"]["input_tokens"]["total"], 140)
        self.assertEqual(baseline["metrics"]["cached_input_tokens"]["total"], 40)
        self.assertEqual(report["cases"][0]["comparison"]["metrics"]["input_tokens"]["difference_candidate_minus_baseline"], -50)

    def test_missing_metrics_are_null_and_disable_difference(self):
        candidate = run_record("cand", "candidate", duration_seconds=None, input_tokens=None, cached_input_tokens=None)
        result = self.report({"schema_version": 1, "runs": [run_record("base"), candidate]})
        report = json.loads(result.stdout)
        metric = report["cases"][0]["candidate"]["metrics"]["duration_seconds"]
        self.assertEqual(metric, {"missing_runs": 1, "observed_runs": 0, "total": None})
        self.assertIsNone(report["cases"][0]["comparison"]["metrics"]["duration_seconds"]["difference_candidate_minus_baseline"])

    def test_environment_mismatch_is_unmatched(self):
        candidate = run_record("cand", "candidate", environment="fixture-v2")
        result = self.report({"schema_version": 1, "runs": [run_record("base"), candidate]})
        report = json.loads(result.stdout)
        self.assertEqual(report["paired_case_count"], 0)
        self.assertEqual(len(report["unmatched"]), 2)

    def test_invalid_records_are_rejected(self):
        invalid = run_record("same", observed_model="actual", model_evidence=None, cached_input_tokens=101)
        result = self.report({"schema_version": 1, "runs": [invalid, run_record("same")]})
        self.assertEqual(result.returncode, 2)
        self.assertIn("model_evidence", result.stderr)

    def test_observed_model_is_never_inferred(self):
        candidate = run_record("cand", "candidate", requested_model="candidate-request")
        result = self.report({"schema_version": 1, "runs": [run_record("base"), candidate]})
        report = json.loads(result.stdout)
        observation = report["cases"][0]["candidate"]["model_observation"]
        self.assertEqual(observation["observed_models"], [])
        self.assertEqual(observation["unobserved_runs"], 1)

    def test_malformed_metrics_and_false_acceptance_are_rejected(self):
        for fields in ({"input_tokens": -1}, {"attempts": True}, {"duration_seconds": float("inf")},
                       {"cached_input_tokens": 101}, {"input_tokens": None}, {"evidence": []},
                       {"checks": []}, {"variant": []}, {"outcome": {}},
                       {"checks": [{"name": "broken", "passed": False, "evidence": "test://fail"}]}):
            with self.subTest(fields=fields):
                result = self.report({"schema_version": 1, "runs": [run_record("bad", **fields)]})
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_duplicate_runs_are_not_double_counted(self):
        record = run_record("duplicate")
        result = self.report({"schema_version": 1, "runs": [record, record]})
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicates", result.stderr)


if __name__ == "__main__":
    unittest.main()
