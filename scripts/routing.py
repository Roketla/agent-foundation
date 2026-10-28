#!/usr/bin/env python3
"""Portable routing decisions and deterministic native agent configuration. No model calls."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TIERS = ("light", "standard", "deep")
EFFORT_ORDER = ("none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra")
EFFORTS = set(EFFORT_ORDER)
# Reviewed capability ceilings for native schema v1; not a live model catalogue.
CODEX_CAPACITY = {"gpt-5.6-luna": 0, "gpt-5.6-terra": 1, "gpt-5.6-sol": 1, "gpt-6-astra": 2}
# Cursor subagent slugs observed for this project. Grok only; not a live catalogue.
CURSOR_CAPACITY = {"cursor-grok-4.6-high-fast": 1, "grok-4.7-xhigh": 2}
# Claude Code subagent models: Haiku light, Sonnet standard (and orchestrator), Opus deep.
CLAUDE_CAPACITY = {"claude-haiku-5-5": 0, "claude-sonnet-5-5": 1, "claude-opus-5-5": 2}
ROLES = {"researcher", "implementer", "reviewer"}
NATIVE_ENGINES = ("codex", "cursor", "claude")
DESCRIPTIONS = {"light": "Narrow, low-risk, well-specified work: lookup, extraction, documentation or small verified changes.",
                "standard": "Bounded implementation, integration, tests and moderate debugging.",
                "deep": "High-risk or ambiguous work, architecture and complex cross-component analysis. Not routine tasks."}


class RoutingError(ValueError):
    pass


def read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RoutingError("Expected a JSON object.")
    return value


def policy(root: Path = ROOT) -> dict:
    p = read(root / "routing/policy.json")
    if p.get("schema_version") != 1 or p.get("tiers") != list(TIERS):
        raise RoutingError("Unsupported routing policy.")
    if any(not isinstance(p.get(key), dict) for key in ("limits", "role_floors", "codex", "cursor", "claude")):
        raise RoutingError("Policy limits, role_floors, codex, cursor and claude must be objects.")
    if set(p["role_floors"]) != ROLES or any(floor not in TIERS for floor in p["role_floors"].values()):
        raise RoutingError("role_floors must give every role a valid tier.")
    for key in ("max_parallel_subagents", "max_delegation_depth", "max_attempts_per_task", "max_handoff_chars", "max_result_chars"):
        if type(p.get("limits", {}).get(key)) is not int or p["limits"][key] < 1:
            raise RoutingError(f"Invalid limit: {key}")
    # A JSON setting cannot enforce paid usage. Do not silently accept pretend budgets.
    if p["limits"].get("token_budget") is not None:
        raise RoutingError("Hard token budgets need a runtime executor; this router does not enforce them.")
    native_block(p["codex"], CODEX_CAPACITY, "Codex")
    native_block(p["cursor"], CURSOR_CAPACITY, "Cursor")
    native_block(p["claude"], CLAUDE_CAPACITY, "Claude")
    return p


def native_block(block: dict, capacity: dict, label: str) -> None:
    if set(block) != set(TIERS):
        raise RoutingError(f"{label} mappings must cover all tiers.")
    for tier in TIERS:
        binding(block[tier])
        value = block[tier]
        if capacity.get(value["model"], -1) < TIERS.index(tier):
            raise RoutingError("Model capacity does not meet the native tier. Review the capacity table before adding models.")
        minimum = ("low", "medium", "high")[TIERS.index(tier)]
        if EFFORT_ORDER.index(value["effort"]) < EFFORT_ORDER.index(minimum):
            raise RoutingError("Native effort is below the tier minimum.")
        if value.get("agent") != "foundation-" + tier:
            raise RoutingError("Unexpected native agent name.")


def binding(value: dict) -> None:
    if not isinstance(value, dict) or not isinstance(value.get("model"), str) or not value["model"].strip():
        raise RoutingError("A model binding requires an exact model ID.")
    if not isinstance(value.get("effort"), str) or value["effort"] not in EFFORTS:
        raise RoutingError("Unsupported reasoning effort.")


def runtime(data: dict, p: dict) -> dict:
    if data.get("schema_version") != 1 or data.get("engine") not in NATIVE_ENGINES + ("pi", "other"):
        raise RoutingError("Unsupported runtime schema or engine.")
    for key in ("can_spawn", "can_select_model", "can_select_effort"):
        if type(data.get(key)) is not bool:
            raise RoutingError(f"Missing boolean capability: {key}")
    if data.get("inventory_source") not in ("session", "catalog", "unverified"):
        raise RoutingError("Inventory source must be session, catalog or unverified.")
    if not isinstance(data.get("current_model"), str):
        raise RoutingError("Current model must be explicit, or an empty string if unknown.")
    if not isinstance(data.get("current_effort"), str) or data["current_effort"] not in EFFORTS | {""}:
        raise RoutingError("Current effort must be observed, or empty if unknown.")
    capacity = data.get("max_parallel_subagents")
    if type(capacity) is not int or capacity < 0:
        raise RoutingError("Runtime concurrency capacity must be an observed nonnegative integer.")
    available = data.get("available_models")
    if not isinstance(available, list):
        raise RoutingError("available_models must be a list.")
    seen = set()
    for item in available:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"] or item["id"] in seen:
            raise RoutingError("Model IDs must be nonempty and unique.")
        seen.add(item["id"])
        if not isinstance(item.get("efforts"), list) or not item["efforts"] or any(not isinstance(e, str) or e not in EFFORTS for e in item["efforts"]):
            raise RoutingError("Every model must declare its supported reasoning efforts.")
    mappings = data.get("tiers")
    if data["engine"] in NATIVE_ENGINES:
        # Custom replacements belong in policy, and must regenerate native configs.
        if "tiers" in data:
            raise RoutingError(f"{data['engine'].title()} tiers come only from policy; omit runtime tiers.")
        mappings = {tier: [p[data["engine"]][tier]] for tier in TIERS}
    if not isinstance(mappings, dict) or set(mappings) != set(TIERS):
        raise RoutingError("Runtime mappings must cover light, standard and deep.")
    for choices in mappings.values():
        if not isinstance(choices, list):
            raise RoutingError("Tier choices must be an ordered list.")
        for choice in choices:
            binding(choice)
    return data | {"tiers": mappings}


def validate_task(task: dict) -> None:
    if not isinstance(task.get("role"), str) or task["role"] not in ROLES or task.get("complexity") not in TIERS:
        raise RoutingError("Invalid role or complexity.")
    if task.get("risk") not in ("low", "medium", "high") or task.get("uncertainty") not in ("low", "medium", "high"):
        raise RoutingError("Risk and uncertainty must be explicit.")
    for key in ("independent", "delegation_worthwhile"):
        if type(task.get(key)) is not bool:
            raise RoutingError(f"Missing boolean task property: {key}")
    for key in ("depth", "active_subagents"):
        if type(task.get(key)) is not int or task[key] < 0:
            raise RoutingError(f"Invalid task counter: {key}")
    attempts = task.get("attempts")
    if not isinstance(attempts, list) or any(not isinstance(a, str) or a not in TIERS for a in attempts):
        raise RoutingError("attempts must list the actual failed tiers, in order.")
    if not isinstance(task.get("objective"), str) or not task["objective"].strip():
        raise RoutingError("A concrete objective is required.")
    for key in ("paths", "acceptance"):
        if not isinstance(task.get(key), list) or not task[key] or any(not isinstance(s, str) or not s.strip() for s in task[key]):
            raise RoutingError(f"A nonempty {key} list is required.")
    if not isinstance(task.get("context", ""), str):
        raise RoutingError("Context must be text.")


def required_tier(task: dict, p: dict) -> str:
    level = max(TIERS.index(task["complexity"]), TIERS.index(p["role_floors"][task["role"]]))
    level = max(level, {"low": 0, "medium": 1, "high": 2}[task["risk"]],
                {"low": 0, "medium": 1, "high": 2}[task["uncertainty"]])
    if task["attempts"]:
        level = max(level, min(2, max(TIERS.index(t) for t in task["attempts"]) + 1))
    return TIERS[level]


def candidates(rt: dict, tier: str) -> list[dict]:
    available = {m["id"]: m["efforts"] for m in rt["available_models"]}
    return [c for c in rt["tiers"][tier] if c["model"] in available and c["effort"] in available[c["model"]]]


def doctor(p: dict, data: dict) -> dict:
    rt = runtime(data, p)
    return {"engine": rt["engine"], "inventory_source": rt["inventory_source"],
            "session_verified": rt["inventory_source"] == "session",
            "can_spawn": rt["can_spawn"], "can_select_model": rt["can_select_model"],
            "can_select_effort": rt["can_select_effort"],
            "effective_parallel_limit": min(p["limits"]["max_parallel_subagents"], rt["max_parallel_subagents"]),
            "tiers": {t: candidates(rt, t) for t in TIERS},
            "hard_token_budget": False,
            "note": "Capabilities are declarations observed by the caller, not probed by this offline command."}


def route(p: dict, data: dict, task: dict) -> dict:
    rt = runtime(data, p)
    validate_task(task)
    limits = p["limits"]
    tier = required_tier(task, p)
    result = {"tier": tier, "role": task["role"], "engine": rt["engine"], "executed": False}
    def finish(action, reason, **fields):
        return result | {"action": action, "reason": reason} | fields
    if len(task["attempts"]) >= limits["max_attempts_per_task"]:
        return finish("stop", "Attempt budget exhausted; reassess the cause and scope before a new task.")
    if rt["inventory_source"] != "session":
        return finish("blocked", "Observe available models and capabilities in the current session first; a bundled catalog is not account access.")
    eligible = candidates(rt, tier)
    if not eligible:
        return finish("blocked", "No available model supports the required tier and effort; do not silently downgrade.")
    choice = eligible[0]
    def active_choice(choices):
        effort = rt["current_effort"]
        for c in choices:
            if c["model"] != rt["current_model"] or not effort:
                continue
            supported = next(m["efforts"] for m in rt["available_models"] if m["id"] == rt["current_model"])
            if effort in supported and EFFORT_ORDER.index(effort) >= EFFORT_ORDER.index(c["effort"]):
                return {"model": rt["current_model"], "effort": effort}
        return None
    may_delegate = task["independent"] and task["delegation_worthwhile"] and task["depth"] < limits["max_delegation_depth"]
    if may_delegate and rt["can_spawn"]:
        if task["active_subagents"] >= min(limits["max_parallel_subagents"], rt["max_parallel_subagents"]):
            return finish("wait", "Concurrency budget reached; collect an existing result before spawning.")
        if not rt["can_select_model"] or not rt["can_select_effort"]:
            inherited = active_choice(eligible)
            if inherited is None:
                return finish("handoff", "Spawner cannot select the required model and effort. Continue in an explicitly selected session.", selection=choice)
            return finish("current", "Binding selection is unavailable; use the verified current model and effort without spawning.", selection=inherited)
        handoff = {key: task.get(key, "") for key in ("role", "objective", "paths", "acceptance", "context")}
        handoff["depth"] = task["depth"] + 1
        handoff["instructions"] = f"No further delegation. Return findings/changes, executed checks and blockers, within {limits['max_result_chars']} characters. Reviewer/researcher assignments do not edit files. Follow the session permissions."
        if len(json.dumps(handoff, ensure_ascii=False)) > limits["max_handoff_chars"]:
            return finish("blocked", "Handoff exceeds the context budget; summarize it without dropping acceptance criteria.")
        return finish("spawn", "Bounded independent task; model and effort verified against the supplied session inventory.", selection=choice, handoff=handoff)
    current = active_choice(eligible)
    if current:
        return finish("current", "Work directly with the observed model and effort; delegation is unavailable, unnecessary or depth-limited.", selection=current)
    # An already active stronger model can do a small task without a new session.
    for stronger in TIERS[TIERS.index(tier) + 1:]:
        current = active_choice(candidates(rt, stronger))
        if current:
            return finish("current", "Observed model and effort meet a higher tier; avoid delegation overhead. This does not reduce its billing rate.", selection=current)
    return finish("handoff", "Required model is available but must be selected explicitly in a suitable session.", selection=choice)


def instructions(p: dict, suffix: str = "") -> str:
    return (f"Read AGENTS.md and the assigned handoff only. Execute its researcher, implementer or reviewer role. Researchers and reviewers do not edit files. Do not delegate further. Preserve scope and session permissions. Return concise evidence, changed paths, checks actually run and blockers within {p['limits']['max_result_chars']} characters. If the task exceeds your tier, return a specific escalation reason instead of guessing. Do not repeat a failed approach. Never claim a model switch or test that did not happen." + suffix)


def agent_markdown(p: dict, engine: str, tier: str, suffix: str = "") -> str:
    value = p[engine][tier]
    header = ["---", f"name: {json.dumps(value['agent'])}", f"model: {json.dumps(value['model'])}"]
    # Claude supports an effort field; Cursor's observed Grok slugs encode it.
    # Keep Cursor's effort in the portable policy, not an unsupported native field.
    if engine == "claude":
        header.append(f"effort: {json.dumps(value['effort'])}")
    header.append(f"description: {json.dumps(DESCRIPTIONS[tier], ensure_ascii=False)}")
    return "\n".join((*header, "---", "", instructions(p, suffix), ""))


def codex_files(p: dict) -> dict[str, str]:
    quote = lambda s: json.dumps(s, ensure_ascii=False)
    standard = p["codex"]["standard"]
    config = f'''# Generated from routing/policy.json by scripts/routing.py. No permission overrides.
model = {quote(standard['model'])}
model_reasoning_effort = {quote(standard['effort'])}

[agents]
enabled = true
max_concurrent_threads_per_session = {p['limits']['max_parallel_subagents']}
default_subagent_model = {quote(standard['model'])}
default_subagent_reasoning_effort = {quote(standard['effort'])}
'''
    output = {".codex/config.toml": config}
    for tier in TIERS:
        value = p["codex"][tier]
        output[f".codex/agents/{value['agent']}.toml"] = "\n".join((
            "# Generated from routing/policy.json.", f"name = {quote(value['agent'])}",
            f"description = {quote(DESCRIPTIONS[tier])}", f"model = {quote(value['model'])}",
            f"model_reasoning_effort = {quote(value['effort'])}", f"developer_instructions = {quote(instructions(p))}", ""))
    return output


def cursor_files(p: dict) -> dict[str, str]:
    manifest = {"schema_version": 1, "engine": "cursor",
                "tiers": {tier: {"model": p["cursor"][tier]["model"], "effort": p["cursor"][tier]["effort"], "agent": p["cursor"][tier]["agent"]} for tier in TIERS}}
    output = {".cursor/model-routing.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"}
    for tier in TIERS:
        output[f".cursor/agents/{p['cursor'][tier]['agent']}.md"] = agent_markdown(p, "cursor", tier, " In Cursor, run this role on the declared Grok model.")
    return output


def claude_files(p: dict) -> dict[str, str]:
    # Sonnet is the session default, so it is the orchestrator; no permission or hook overrides.
    settings = {"model": p["claude"]["standard"]["model"]}
    output = {".claude/settings.json": json.dumps(settings, ensure_ascii=False, indent=2) + "\n"}
    for tier in TIERS:
        output[f".claude/agents/{p['claude'][tier]['agent']}.md"] = agent_markdown(p, "claude", tier)
    return output


def validate(root: Path = ROOT) -> dict:
    p = policy(root)
    expected = codex_files(p) | cursor_files(p) | claude_files(p)
    for relative, content in expected.items():
        path = root / relative
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise RoutingError(f"Native config drift: {relative}. Review and regenerate with render-codex, render-cursor or render-claude.")
    for engine in NATIVE_ENGINES:
        extension = "toml" if engine == "codex" else "md"
        for tier in TIERS:
            legacy = root / f".{engine}/agents/foundation_{tier}.{extension}"
            if legacy.exists():
                raise RoutingError(f"Obsolete native agent: {legacy.relative_to(root)}. Migrate to foundation-{tier} before removing it.")
    return {"valid": True, "codex_configs": 4, "cursor_configs": 4, "claude_configs": 4, "hard_token_budget": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("render-codex", help="Emit generated files as JSON; review before writing .codex/.")
    sub.add_parser("render-cursor", help="Emit generated files as JSON; review before writing .cursor/.")
    sub.add_parser("render-claude", help="Emit generated files as JSON; review before writing .claude/.")
    for command in ("doctor", "route"):
        cmd = sub.add_parser(command)
        cmd.add_argument("--runtime", required=True, type=Path)
        if command == "route":
            cmd.add_argument("--task", required=True, type=Path)
    args = parser.parse_args()
    try:
        p = policy()
        if args.command == "validate":
            result = validate()
        elif args.command == "render-codex":
            result = codex_files(p)
        elif args.command == "render-cursor":
            result = cursor_files(p)
        elif args.command == "render-claude":
            result = claude_files(p)
        elif args.command == "doctor":
            result = doctor(p, read(args.runtime))
        else:
            result = route(p, read(args.runtime), read(args.task))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result.get("action") in ("blocked", "stop", "handoff", "wait") else 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Routing error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
