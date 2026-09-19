import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts import continuity as c

REPO = Path(__file__).resolve().parents[1]


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "src").mkdir()
        (self.root / "src/site.js").write_text("const contactMode = 'mailto';\n")
        self.plan = {"objective": "Web corporativa", "tasks": [
            {"id": "build", "title": "Implementar contacte", "status": "in_progress", "acceptance": ["Enllaç funcional"], "blockers": [], "evidence": []},
            {"id": "verify", "title": "Verificar navegació", "status": "pending", "acceptance": ["Flux revisat"], "blockers": [], "evidence": []}],
            "next_action": "Acabar el contacte i verificar el flux"}

    def save(self, **changes):
        return c.save(self.root, {"expected_revision": c.load(self.root)["revision"], **changes})

    def note(self):
        return {"id": "contact", "claim": "El contacte usa mailto.", "sources": [{"path": "src/site.js", "quote": "contactMode = 'mailto'"}]}

    def test_empty_template_has_no_invented_memory(self):
        self.assertEqual(c.resume(self.root)["phase"], "empty")
        self.assertFalse((self.root / "project/work.json").exists())

    def test_fresh_process_recovers_exact_next_action_and_blocker(self):
        self.plan["tasks"][0].update(status="blocked", blockers=["Falta adreça aprovada"])
        self.save(plan=self.plan)
        result = subprocess.run([sys.executable, str(REPO / "scripts/continuity.py"), "--root", str(self.root), "resume"], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        self.assertEqual(data["next_action"], self.plan["next_action"])
        self.assertEqual(data["tasks"][0]["blockers"], ["Falta adreça aprovada"])

    def test_concurrent_stale_update_cannot_overwrite_new_work(self):
        self.save(plan=self.plan)
        with self.assertRaisesRegex(c.ContinuityError, "revision"):
            c.save(self.root, {"expected_revision": 0, "plan": self.plan})
        self.assertEqual(c.load(self.root)["revision"], 1)

    def test_lock_prevents_simultaneous_writers(self):
        (self.root / "project").mkdir()
        (self.root / "project/.work.lock").write_text("other writer")
        with self.assertRaises(c.ContinuityError):
            self.save(plan=self.plan)
        self.assertFalse((self.root / "project/work.json").exists())

    def test_memory_requires_real_evidence_and_duplicates_fail(self):
        self.save(plan=self.plan, memory_upserts=[self.note()])
        self.assertEqual(len(c.resume(self.root)["memory"]), 1)
        bad = self.note() | {"id": "duplicate"}
        with self.assertRaises(c.ContinuityError):
            self.save(memory_upserts=[bad])
        bad = self.note() | {"sources": [{"path": "src/site.js", "quote": "invented"}]}
        with self.assertRaises(c.ContinuityError):
            self.save(memory_upserts=[bad])

    def test_changed_source_excludes_claim_until_reverified(self):
        self.save(plan=self.plan, memory_upserts=[self.note()])
        (self.root / "src/site.js").write_text("const contactMode = 'form';\n")
        data = c.resume(self.root)
        self.assertEqual(data["memory"], [])
        self.assertEqual(data["stale_memory"], ["contact"])
        self.save(memory_upserts=[self.note() | {"claim": "El contacte usa formulari.", "sources": [{"path": "src/site.js", "quote": "contactMode = 'form'"}]}])
        self.assertEqual(c.resume(self.root)["stale_memory"], [])

    def test_source_deletion_and_symlink_cannot_be_fresh_evidence(self):
        self.save(plan=self.plan, memory_upserts=[self.note()])
        path = self.root / "src/site.js"
        path.unlink()
        self.assertEqual(c.resume(self.root)["stale_memory"], ["contact"])
        path.symlink_to(REPO / "README.md")
        with self.assertRaises(ValueError):
            self.save(memory_upserts=[self.note()])

    def test_secret_and_nonproject_sources_rejected(self):
        for path in ("../outside", "/tmp/file", ".env", ".local/transcript.json"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.save(memory_upserts=[self.note() | {"sources": [{"path": path, "quote": "x"}]}])
        with self.assertRaises(c.ContinuityError):
            self.save(plan=self.plan | {"objective": "ghp_" + "a" * 36})

    def test_done_requires_evidence_and_completed_plan_has_no_pending_action(self):
        self.plan["tasks"][0]["status"] = "done"
        with self.assertRaises(c.ContinuityError):
            self.save(plan=self.plan)
        for task in self.plan["tasks"]:
            task.update(status="done", evidence=["src/site.js"])
        self.plan["next_action"] = ""
        self.save(plan=self.plan)
        self.assertEqual(c.resume(self.root)["phase"], "complete")
        (self.root / "src/site.js").write_text("changed")
        self.assertEqual(c.resume(self.root)["phase"], "needs_review")

    def test_invalid_plan_does_not_modify_current_state(self):
        self.save(plan=self.plan)
        original = (self.root / "project/work.json").read_bytes()
        for plan in (self.plan | {"tasks": self.plan["tasks"] * 2}, self.plan | {"next_action": ""}, self.plan | {"tasks": []}):
            with self.assertRaises(c.ContinuityError):
                self.save(plan=plan)
            self.assertEqual((self.root / "project/work.json").read_bytes(), original)

    def test_memory_has_limits_and_explicit_forget(self):
        self.save(plan=self.plan, memory_upserts=[self.note()])
        with self.assertRaises(c.ContinuityError):
            self.save(memory_upserts=[self.note() | {"claim": "x" * 501}])
        self.save(forget=["contact"])
        self.assertEqual(c.resume(self.root)["memory"], [])

    def test_oversized_resume_does_not_commit_an_unreadable_plan(self):
        self.save(plan=self.plan)
        before = (self.root / c.STORE).read_bytes()
        tasks = [{"id": f"task-{i}", "title": "x" * 120, "status": "blocked",
                  "acceptance": ["Check"], "blockers": ["x" * 400] * 2, "evidence": []}
                 for i in range(12)]
        with self.assertRaisesRegex(c.ContinuityError, "Resume budget"):
            self.save(plan={"objective": "x" * 400, "tasks": tasks, "next_action": "x" * 400})
        self.assertEqual((self.root / c.STORE).read_bytes(), before)

    def test_unrelated_save_cannot_refresh_completed_task_evidence(self):
        self.plan["tasks"][0].update(status="done", evidence=["src/site.js"])
        self.save(plan=self.plan)
        (self.root / "src/site.js").write_text("changed")
        self.save()
        self.assertEqual(c.resume(self.root)["stale_tasks"], ["build"])
        self.save(recheck_tasks=["build"])
        self.assertEqual(c.resume(self.root)["stale_tasks"], [])


if __name__ == "__main__":
    unittest.main()
