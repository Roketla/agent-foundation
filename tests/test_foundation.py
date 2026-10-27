"""Behavioral tests of onboarding and preservation of existing project work."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("foundation", REPO / "scripts/foundation.py")
foundation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foundation)

ANSWERS = {
    "name": "Estudi Blau",
    "profile": "corporate",
    "purpose": "Presentar serveis i rebre sol·licituds de pressupost.",
    "audience": "Petites empreses locals",
    "mvp": ["Pàgina de serveis", "Formulari de contacte"],
    "acceptance": ["Enviar el formulari mostra confirmació i no duplica la petició."],
    "languages": ["ca", "es"],
}


class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ("project", "profiles"):
            shutil.copytree(REPO / folder, self.root / folder)
        # Tests also work in a product cloned from this template, after onboarding.
        blank = {k: [] if k in foundation.LISTS else "" for k in foundation.FIELDS}
        blank.update(schema_version=1, stack="undecided", hosting="undecided", data_sensitivity="undecided")
        (self.root / "project/brief.json").write_bytes(foundation.encoded(blank))
        (self.root / "project/state.json").unlink(missing_ok=True)

    def complete(self, profile="corporate"):
        foundation.configure(self.root, ANSWERS | {"profile": profile})

    def test_blank_template_does_not_initialize_itself(self):
        self.assertEqual(foundation.status(self.root)["phase"], "uninitialized")
        with self.assertRaises(foundation.FoundationError):
            foundation.initialize(self.root)
        self.assertFalse((self.root / "docs").exists())

    def test_partial_answers_resume_without_losing_existing_information(self):
        foundation.configure(self.root, {"name": "Projecte català"})
        self.assertEqual(foundation.status(self.root)["phase"], "in_progress")
        foundation.configure(self.root, {"audience": "Cooperatives"})
        data = foundation.load_brief(self.root)
        self.assertEqual(data["name"], "Projecte català")
        self.assertEqual(data["audience"], "Cooperatives")

    def test_all_profiles_generate_their_own_controls(self):
        for profile in foundation.PROFILES:
            with self.subTest(profile=profile):
                self.complete(profile)
                result = foundation.initialize(self.root, refresh=True)
                self.assertEqual(result["phase"], "ready")
                quality = (self.root / "docs/project/quality.md").read_text()
                profile_data = foundation.read_json(self.root / f"profiles/{profile}.json")
                self.assertIn(profile_data["checks"][0], quality)
                self.assertIn("Estudi Blau", (self.root / "docs/project/brief.md").read_text())

    def test_every_profile_file_is_registered(self):
        files = sorted(path.stem for path in (self.root / "profiles").glob("*.json"))
        self.assertEqual(files, sorted(foundation.PROFILES))

    def test_initialization_is_idempotent(self):
        self.complete()
        foundation.initialize(self.root)
        snapshots = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        foundation.initialize(self.root)
        self.assertEqual(snapshots, {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_partial_generation_resumes_if_documents_are_identical(self):
        self.complete()
        generated = foundation.render(self.root, foundation.load_brief(self.root))
        first = self.root / foundation.GENERATED[0]
        first.parent.mkdir(parents=True)
        first.write_bytes(generated[foundation.GENERATED[0]])
        self.assertEqual(foundation.initialize(self.root)["phase"], "ready")

    def test_existing_document_conflict_changes_nothing(self):
        self.complete()
        path = self.root / "docs/project/plan.md"
        path.parent.mkdir(parents=True)
        path.write_text("Treball manual valuós")
        with self.assertRaisesRegex(foundation.FoundationError, "Conflicte"):
            foundation.initialize(self.root)
        self.assertEqual(path.read_text(), "Treball manual valuós")
        self.assertFalse((self.root / "docs/project/brief.md").exists())
        self.assertFalse((self.root / "project/state.json").exists())

    def test_changed_brief_requires_refresh(self):
        self.complete()
        foundation.initialize(self.root)
        foundation.configure(self.root, {"purpose": "Nova proposta"})
        self.assertEqual(foundation.status(self.root)["phase"], "in_progress")
        with self.assertRaises(foundation.FoundationError):
            foundation.initialize(self.root)
        self.assertEqual(foundation.initialize(self.root, refresh=True)["phase"], "ready")
        self.assertIn("Nova proposta", (self.root / "docs/project/brief.md").read_text())

    def test_refresh_preserves_manual_changes_and_other_documents(self):
        self.complete()
        foundation.initialize(self.root)
        manual = self.root / "docs/project/plan.md"
        manual.write_text("Canvi manual")
        original_brief = (self.root / "docs/project/brief.md").read_bytes()
        foundation.configure(self.root, {"name": "Un altre nom"})
        with self.assertRaises(foundation.FoundationError):
            foundation.initialize(self.root, refresh=True)
        self.assertEqual(manual.read_text(), "Canvi manual")
        self.assertEqual((self.root / "docs/project/brief.md").read_bytes(), original_brief)

    def test_manual_notes_do_not_restart_interview(self):
        self.complete()
        foundation.initialize(self.root)
        (self.root / "docs/project/notes.md").write_text("Notes de la primera reunió")
        self.assertEqual(foundation.status(self.root)["phase"], "ready")

    def test_missing_generated_document_is_not_ready(self):
        self.complete()
        foundation.initialize(self.root)
        (self.root / "docs/project/quality.md").unlink()
        self.assertEqual(foundation.status(self.root)["phase"], "in_progress")
        self.assertEqual(foundation.initialize(self.root)["phase"], "ready")

    def test_invalid_input_does_not_write(self):
        original = (self.root / "project/brief.json").read_bytes()
        for payload in ({"profile": "../../outside"}, {"mvp": "not a list"}, {"languages": [3]},
                        {"schema_version": True}, {"unknown": "data"}, {"acceptance": [""]}):
            with self.subTest(payload=payload), self.assertRaises(foundation.FoundationError):
                foundation.configure(self.root, payload)
            self.assertEqual((self.root / "project/brief.json").read_bytes(), original)

    def test_known_secret_patterns_rejected_without_echo(self):
        secret = "ghp_" + "a" * 36
        with self.assertRaises(foundation.FoundationError) as caught:
            foundation.configure(self.root, {"constraints": [secret]})
        self.assertNotIn(secret, str(caught.exception))

    def test_symlink_destination_cannot_write_outside_checkout(self):
        self.complete()
        with tempfile.TemporaryDirectory() as outside:
            try:
                (self.root / "docs").symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("Symlink creation unavailable")
            with self.assertRaises(foundation.FoundationError):
                foundation.initialize(self.root)
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_lists_replace_instead_of_accumulating_stale_requirements(self):
        self.complete()
        foundation.configure(self.root, {"mvp": ["Només catàleg"]})
        self.assertEqual(foundation.load_brief(self.root)["mvp"], ["Només catàleg"])

    def test_complete_cli_flow_operates_on_the_cloned_repository(self):
        shutil.copytree(REPO / "scripts", self.root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        answers = self.root / "answers.json"
        answers.write_bytes(foundation.encoded(ANSWERS))
        command = [sys.executable, str(self.root / "scripts/foundation.py")]
        def run(*args):
            result = subprocess.run(command + list(args), cwd=self.root, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        self.assertEqual(run("configure", "--answers", str(answers))["phase"], "in_progress")
        self.assertIn("preview", run("plan"))
        self.assertFalse((self.root / "docs").exists())
        self.assertEqual(run("init")["phase"], "ready")
        self.assertEqual(run("status")["phase"], "ready")


class RepositoryTests(unittest.TestCase):
    def test_installed_skills_integrity(self):
        self.assertGreater(foundation.verify_skills(REPO), 0)

    def test_tampering_and_untracked_vendor_files_fail_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "vendor").mkdir()
            (root / "skills").mkdir()
            file = root / "vendor/source.md"
            file.write_text("Original")
            lock = {"schema_version": 1, "files": {"vendor/source.md": foundation.digest(file.read_bytes())}}
            (root / "skills/lock.json").write_bytes(foundation.encoded(lock))
            foundation.verify_skills(root)
            file.write_text("Modified")
            with self.assertRaises(foundation.FoundationError):
                foundation.verify_skills(root)
            file.write_text("Original")
            (root / "vendor/extra.md").write_text("Unreviewed")
            with self.assertRaises(foundation.FoundationError):
                foundation.verify_skills(root)

    def test_cli_status_is_machine_readable(self):
        result = subprocess.run([sys.executable, str(REPO / "scripts/foundation.py"), "status"], capture_output=True, text=True, check=True)
        self.assertIn(json.loads(result.stdout)["phase"], ("uninitialized", "in_progress", "ready"))

    def test_repository_validation(self):
        self.assertTrue(foundation.validate(REPO)["valid"])


if __name__ == "__main__":
    unittest.main()
