"""Decisions are tested without making paid calls or spawning real models."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts import routing as r

ROOT = Path(__file__).resolve().parents[1]


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.policy = r.policy()
        self.runtime = {
            "schema_version": 1, "engine": "codex", "inventory_source": "session",
            "current_model": "gpt-5.6-terra", "can_spawn": True, "can_select_model": True,
            "current_effort": "medium", "can_select_effort": True, "max_parallel_subagents": 2,
            "available_models": [{"id": m["model"], "efforts": [m["effort"]]} for m in self.policy["codex"].values()],
        }
        self.task = r.read(ROOT / "routing/task.example.json")

    def route(self, **changes):
        return r.route(self.policy, self.runtime, self.task | changes)

    def test_clear_small_change_uses_luna(self):
        result = self.route()
        self.assertEqual(result["action"], "spawn")
        self.assertEqual(result["selection"]["model"], "gpt-5.6-luna")
        self.assertEqual(result["selection"]["effort"], "low")
        self.assertFalse(result["executed"])

    def test_routine_implementation_uses_terra(self):
        self.assertEqual(self.route(complexity="standard")["selection"]["model"], "gpt-5.6-terra")

    def test_high_risk_small_diff_goes_directly_to_astra(self):
        result = self.route(risk="high")
        self.assertEqual(result["tier"], "deep")
        self.assertEqual(result["selection"]["model"], "gpt-6-astra")

    def test_high_uncertainty_goes_directly_to_astra(self):
        self.assertEqual(self.route(uncertainty="high")["tier"], "deep")

    def test_medium_risk_does_not_use_luna(self):
        self.assertEqual(self.route(risk="medium")["tier"], "standard")

    def test_roles_are_independent_of_tier(self):
        for role in r.ROLES:
            self.assertEqual(self.route(role=role, risk="high")["selection"]["model"], "gpt-6-astra")

    def test_failed_attempt_escalates_with_a_global_attempt_budget(self):
        self.assertEqual(self.route(attempts=["light"])["tier"], "standard")
        self.assertEqual(self.route(attempts=["standard"])["tier"], "deep")
        self.assertEqual(self.route(attempts=["light", "standard"])["action"], "stop")
        self.assertEqual(self.route(attempts=["deep", "deep"])["action"], "stop")

    def test_no_silent_downgrade_when_deep_model_missing(self):
        self.runtime["available_models"] = self.runtime["available_models"][:2]
        self.assertEqual(self.route(risk="high")["action"], "blocked")

    def test_unsupported_effort_is_not_silently_inherited(self):
        self.runtime["available_models"][0]["efforts"] = ["medium"]
        self.assertEqual(self.route()["action"], "blocked")

    def test_catalog_is_not_evidence_of_account_access(self):
        for source in ("catalog", "unverified"):
            self.runtime["inventory_source"] = source
            self.assertEqual(self.route()["action"], "blocked")

    def test_parallel_limit_waits(self):
        self.assertEqual(self.route(active_subagents=2)["action"], "wait")
        self.runtime["max_parallel_subagents"] = 1
        self.assertEqual(self.route(active_subagents=1)["action"], "wait")

    def test_current_model_support_is_not_current_reasoning_effort(self):
        self.runtime["current_model"] = "gpt-6-astra"
        self.runtime["available_models"][2]["efforts"] = ["low", "high", "xhigh"]
        for effort in ("low", ""):
            self.runtime["current_effort"] = effort
            self.assertEqual(self.route(risk="high", independent=False)["action"], "handoff")
        self.runtime["current_effort"] = "xhigh"
        result = self.route(risk="high", independent=False)
        self.assertEqual(result["action"], "current")
        self.assertEqual(result["selection"]["effort"], "xhigh")

    def test_no_effort_selection_cannot_request_an_unappliable_binding(self):
        self.runtime["can_select_effort"] = False
        self.assertEqual(self.route()["action"], "handoff")

    def test_malformed_nested_structures_are_validation_errors(self):
        for changes in ({"role": []}, {"attempts": [[]]}):
            with self.assertRaises(r.RoutingError):
                self.route(**changes)
        self.runtime["available_models"][0]["efforts"] = [[]]
        with self.assertRaises(r.RoutingError):
            self.route()

    def test_codex_mapping_cannot_be_overridden_in_runtime(self):
        self.runtime["tiers"] = 42
        with self.assertRaises(r.RoutingError):
            self.route()

    def test_depth_limit_never_creates_grandchildren(self):
        self.assertEqual(self.route(depth=1)["action"], "current")
        self.runtime["current_model"] = "gpt-5.6-luna"
        self.assertEqual(self.route(depth=1, risk="high")["action"], "handoff")

    def test_no_delegation_for_dependent_or_tiny_task(self):
        self.assertEqual(self.route(independent=False)["action"], "current")
        self.assertEqual(self.route(delegation_worthwhile=False)["action"], "current")

    def test_no_model_selection_does_not_pretend_to_spawn(self):
        self.runtime["can_select_model"] = False
        self.assertEqual(self.route()["action"], "handoff")
        self.assertEqual(self.route(complexity="standard")["action"], "current")

    def test_handoff_has_only_bounded_task_context(self):
        result = self.route()
        self.assertEqual(result["handoff"]["depth"], 1)
        self.assertNotIn("available_models", result["handoff"])
        self.assertEqual(result["handoff"]["acceptance"], self.task["acceptance"])
        self.assertEqual(self.route(context="x" * 8000)["action"], "blocked")

    def test_cursor_selects_grok_by_tier(self):
        self.runtime.update(engine="cursor", current_model="cursor-grok-4.6-high-fast", current_effort="high",
            available_models=[{"id": "cursor-grok-4.6-high-fast", "efforts": ["high"]},
                              {"id": "grok-4.7-xhigh", "efforts": ["xhigh"]}])
        self.assertEqual(self.route()["selection"]["model"], "cursor-grok-4.6-high-fast")
        self.assertEqual(self.route()["selection"]["effort"], "high")
        deep = self.route(risk="high")
        self.assertEqual(deep["tier"], "deep")
        self.assertEqual(deep["selection"]["model"], "grok-4.7-xhigh")
        self.assertEqual(deep["selection"]["effort"], "xhigh")

    def test_cursor_mapping_cannot_be_overridden_in_runtime(self):
        self.runtime.update(engine="cursor", tiers={"light": [], "standard": [], "deep": []})
        with self.assertRaises(r.RoutingError):
            self.route()

    def test_cursor_does_not_silently_downgrade_when_deep_grok_is_missing(self):
        self.runtime.update(engine="cursor", current_model="cursor-grok-4.6-high-fast", current_effort="high",
            available_models=[{"id": "cursor-grok-4.6-high-fast", "efforts": ["high"]}])
        self.assertEqual(self.route(risk="high")["action"], "blocked")

    def claude_runtime(self, models=None):
        models = models or {"claude-haiku-5-5": "low", "claude-sonnet-5-5": "medium", "claude-opus-5-5": "high"}
        self.runtime.update(engine="claude", current_model="claude-sonnet-5-5", current_effort="medium",
                            available_models=[{"id": m, "efforts": [e]} for m, e in models.items()])
        self.runtime.pop("tiers", None)

    def test_claude_selects_haiku_sonnet_opus_by_tier(self):
        self.claude_runtime()
        self.assertEqual(self.route()["selection"]["model"], "claude-haiku-5-5")
        self.assertEqual(self.route(complexity="standard")["selection"]["model"], "claude-sonnet-5-5")
        self.assertEqual(self.route(risk="high")["selection"]["model"], "claude-opus-5-5")

    def test_claude_orchestrator_works_directly_when_task_is_standard(self):
        self.claude_runtime()
        result = self.route(complexity="standard", independent=False)
        self.assertEqual(result["action"], "current")
        self.assertEqual(result["selection"]["model"], "claude-sonnet-5-5")

    def test_claude_does_not_silently_downgrade_when_opus_is_missing(self):
        self.claude_runtime({"claude-haiku-5-5": "low", "claude-sonnet-5-5": "medium"})
        self.assertEqual(self.route(risk="high")["action"], "blocked")

    def test_claude_mapping_cannot_be_overridden_in_runtime(self):
        self.claude_runtime()
        self.runtime["tiers"] = {"light": [], "standard": [], "deep": []}
        with self.assertRaises(r.RoutingError):
            self.route()

    def test_reviewer_is_always_deep_and_researcher_at_least_standard(self):
        self.claude_runtime()
        self.assertEqual(self.route(role="reviewer")["selection"]["model"], "claude-opus-5-5")
        self.assertEqual(self.route(role="researcher")["selection"]["model"], "claude-sonnet-5-5")
        self.assertEqual(self.route(role="implementer")["selection"]["model"], "claude-haiku-5-5")

    def test_other_provider_uses_explicit_mapping_and_skips_unavailable_preference(self):
        self.runtime.update(engine="other", current_model="provider/balanced", available_models=[
            {"id": "provider/fast", "efforts": ["none"]}, {"id": "provider/balanced", "efforts": ["medium"]}],
            tiers={"light": [{"model": "provider/missing", "effort": "none"}, {"model": "provider/fast", "effort": "none"}],
                   "standard": [{"model": "provider/balanced", "effort": "medium"}], "deep": []})
        self.assertEqual(self.route()["selection"]["model"], "provider/fast")
        self.assertEqual(self.route(risk="high")["action"], "blocked")

    def test_pi_without_extension_falls_back_to_current_or_handoff(self):
        self.runtime.update(engine="pi", can_spawn=False, tiers={t: [m] for t, m in self.policy["codex"].items()})
        self.assertEqual(self.route()["action"], "current")
        self.assertEqual(self.route(risk="high")["action"], "handoff")

    def test_unknown_capability_and_malformed_tasks_fail(self):
        for changes in ({"risk": "unknown"}, {"depth": True}, {"attempts": "light"},
                        {"paths": []}, {"complexity": "cheap"}, {"independent": "yes"}):
            with self.subTest(changes=changes), self.assertRaises(r.RoutingError):
                self.route(**changes)
        self.runtime["can_spawn"] = "yes"
        with self.assertRaises(r.RoutingError):
            self.route()

    def test_duplicate_model_ids_rejected(self):
        self.runtime["available_models"].append(copy.deepcopy(self.runtime["available_models"][0]))
        with self.assertRaises(r.RoutingError):
            self.route()

    def test_cli_exit_code_for_unverified_inventory(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/routing.py"), "route",
            "--runtime", str(ROOT / "routing/runtime.example.json"), "--task", str(ROOT / "routing/task.example.json")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["action"], "blocked")


class NativeConfigTests(unittest.TestCase):
    def test_native_policy_cannot_accidentally_weaken_deep_tier(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "routing").mkdir()
            for changes in ({"model": "gpt-5.6-luna"}, {"effort": "low"}):
                p = r.policy()
                p["codex"]["deep"].update(changes)
                (root / "routing/policy.json").write_text(json.dumps(p))
                with self.assertRaises(r.RoutingError):
                    r.policy(root)

    def test_malformed_policy_containers_have_clear_validation_errors(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "routing").mkdir()
            for field in ("limits", "codex"):
                p = r.policy()
                p[field] = []
                (root / "routing/policy.json").write_text(json.dumps(p))
                with self.assertRaises(r.RoutingError):
                    r.policy(root)

    def test_repository_native_configuration_matches_policy(self):
        self.assertTrue(r.validate()["valid"])

    def test_no_permission_or_provider_overrides_are_generated(self):
        files = r.codex_files(r.policy()) | r.cursor_files(r.policy()) | r.claude_files(r.policy())
        for content in files.values():
            for key in ("sandbox_mode =", "approval_policy =", "model_provider =", "api_key"):
                self.assertNotIn(key, content)

    def test_drift_and_fictitious_hard_budgets_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "routing").mkdir()
            p = r.policy()
            (root / "routing/policy.json").write_text(json.dumps(p))
            for name, content in (r.codex_files(p) | r.cursor_files(p) | r.claude_files(p)).items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            r.validate(root)
            (root / ".codex/config.toml").write_text("model = 'other'")
            with self.assertRaises(r.RoutingError):
                r.validate(root)
            p["limits"]["token_budget"] = 1000
            (root / "routing/policy.json").write_text(json.dumps(p))
            with self.assertRaises(r.RoutingError):
                r.policy(root)

    def test_claude_deep_tier_cannot_use_sonnet_and_floors_are_required(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "routing").mkdir()
            p = r.policy()
            p["claude"]["deep"]["model"] = "claude-sonnet-5-5"
            (root / "routing/policy.json").write_text(json.dumps(p))
            with self.assertRaises(r.RoutingError):
                r.policy(root)
            p = r.policy()
            del p["role_floors"]["reviewer"]
            (root / "routing/policy.json").write_text(json.dumps(p))
            with self.assertRaises(r.RoutingError):
                r.policy(root)

    def test_cursor_deep_tier_cannot_use_the_standard_grok(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "routing").mkdir()
            p = r.policy()
            p["cursor"]["deep"]["model"] = "cursor-grok-4.6-high-fast"
            (root / "routing/policy.json").write_text(json.dumps(p))
            with self.assertRaises(r.RoutingError):
                r.policy(root)


if __name__ == "__main__":
    unittest.main()
