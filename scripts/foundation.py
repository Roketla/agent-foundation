#!/usr/bin/env python3
"""Onboarding determinista, offline i sense dependències de tercers (Python 3.10+)."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STRINGS = {"name", "profile", "purpose", "audience", "stack", "hosting", "data_sensitivity"}
LISTS = {"mvp", "out_of_scope", "acceptance", "languages", "integrations", "constraints", "open_questions"}
FIELDS = STRINGS | LISTS | {"schema_version"}
REQUIRED = ("name", "profile", "purpose", "audience", "mvp", "acceptance", "languages")
GENERATED = ("docs/project/brief.md", "docs/project/architecture.md", "docs/project/quality.md", "docs/project/plan.md")
SECRET = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,}|AKIA[A-Z0-9]{16})")


class FoundationError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def local(root: Path, relative: str) -> Path:
    """Refuse traversal and symlinks, even symlinks resolving inside the repo."""
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise FoundationError(f"Ruta no local: {relative}")
    current = root.resolve()
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise FoundationError(f"Enllaç simbòlic no admès: {relative}")
    return current


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FoundationError(f"S'esperava un objecte JSON: {path.name}")
    return value


def write_atomic(path: Path, content: bytes) -> None:
    # Unique temporary file in the same directory; never follow a preexisting link.
    import os
    import tempfile
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".foundation-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
        Path(temp).replace(path)
    finally:
        Path(temp).unlink(missing_ok=True)


def check_fields(data: dict, partial: bool = False) -> None:
    extra = set(data) - FIELDS
    if extra:
        # Do not echo potentially sensitive values or unknown keys.
        raise FoundationError("Hi ha camps desconeguts; consulta project/brief.json.")
    if not partial and set(data) != FIELDS:
        raise FoundationError("Falten camps de l'esquema del brief.")
    if "schema_version" in data and (type(data["schema_version"]) is not int or data["schema_version"] != 1):
        raise FoundationError("Versió d'esquema no compatible.")
    for key, value in data.items():
        if key in STRINGS and not isinstance(value, str):
            raise FoundationError(f"{key} ha de ser text.")
        if key in LISTS and (not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value)):
            raise FoundationError(f"{key} ha de ser una llista de textos no buits.")
    if SECRET.search(json.dumps(data)):
        raise FoundationError("Possible secret: no el desis al brief. Usa només el nom de la variable.")


def load_brief(root: Path) -> dict:
    data = read_json(local(root, "project/brief.json"))
    check_fields(data)
    profile = data["profile"]
    if profile and profile not in ("corporate", "ecommerce", "saas"):
        raise FoundationError("Perfil desconegut: corporate, ecommerce o saas.")
    return data


def missing(data: dict) -> list[str]:
    return [key for key in REQUIRED if not data[key] or (isinstance(data[key], str) and not data[key].strip())]


def load_state(root: Path) -> dict:
    path = local(root, "project/state.json")
    if not path.exists():
        return {}
    state = read_json(path)
    if state.get("schema_version") != 1 or not isinstance(state.get("files"), dict) or set(state["files"]) != set(GENERATED):
        raise FoundationError("Estat inconsistent; revisa project/state.json sense eliminar documents.")
    return state


def status(root: Path) -> dict:
    data, state = load_brief(root), load_state(root)
    absent = missing(data)
    initialized = bool(state)
    complete = initialized and not absent and state.get("brief_sha256") == digest(encoded(data))
    complete = complete and all(local(root, path).is_file() for path in GENERATED)
    phase = "ready" if complete else "in_progress" if initialized or any(data[k] for k in REQUIRED) else "uninitialized"
    return {"phase": phase, "missing": absent, "profile": data["profile"] or None,
            "next": "Treballa sobre la tasca del projecte." if complete else "Completa el brief i executa plan i init; usa --refresh si ja hi ha documents generats."}


def configure(root: Path, answers: dict) -> dict:
    check_fields(answers, partial=True)
    load_state(root)
    data = load_brief(root) | answers
    check_fields(data)
    if data["profile"] and data["profile"] not in ("corporate", "ecommerce", "saas"):
        raise FoundationError("Perfil desconegut.")
    write_atomic(local(root, "project/brief.json"), encoded(data))
    return status(root)


def bullets(values: list[str]) -> str:
    return "\n".join(f"- {v}" for v in values) if values else "- Pendent de concretar."


def render(root: Path, data: dict) -> dict[str, bytes]:
    absent = missing(data)
    if absent:
        raise FoundationError("Falten respostes: " + ", ".join(absent))
    profile = read_json(local(root, f"profiles/{data['profile']}.json"))
    header = "<!-- Generat des de project/brief.json. Notes manuals a docs/project/notes.md. -->\n\n"
    brief = f"# {data['name']}\n\n{data['purpose']}\n\n## Públic\n\n{data['audience']}\n\n## Perfil\n\n{profile['label']}\n\n## MVP\n\n{bullets(data['mvp'])}\n\n## Fora d'abast\n\n{bullets(data['out_of_scope'])}\n\n## Acceptació acordada\n\n{bullets(data['acceptance'])}\n\n## Idiomes\n\n{bullets(data['languages'])}\n\n## Restriccions\n\n{bullets(data['constraints'])}\n\n## Preguntes obertes\n\n{bullets(data['open_questions'])}\n"
    architecture = f"# Arquitectura inicial\n\nStack: {data['stack']}\n\nHosting: {data['hosting']}\n\nSensibilitat de dades: {data['data_sensitivity']}\n\n## Integracions\n\n{bullets(data['integrations'])}\n\n## Riscos a revisar\n\n{bullets(profile['risks'])}\n\nLes opcions undecided són decisions pendents, no valors per defecte. Abans d'implementar, concreta el mínim stack necessari i registra decisions significatives a docs/adr/.\n"
    quality = f"# Qualitat del projecte\n\n## Criteris del negoci\n\n{bullets(data['acceptance'])}\n\n## Comprovacions proposades pel perfil\n\n{bullets(profile['checks'])}\n\n## Skills disponibles\n\nLes set skills de base són a skills/catalog.json; activa-les per tasca, no totes a cada torn. Les de React i rendiment són opcionals i encara no estan instal·lades.\n\n## Verificació\n\nQuan existeixi codi, afegeix les ordres reals de lint, tipus i tests a la CI del producte. La CI de foundation només valida aquesta base. Defineix proves del flux crític i dels permisos. Una auditoria pendent no és una auditoria superada.\n"
    plan = "# Primer increment\n\n1. Resoldre les preguntes que bloquegin el primer flux.\n2. Proposar el stack mínim i un ADR si hi ha una decisió significativa.\n3. Implementar un recorregut complet del MVP, amb estats buits i errors.\n4. Verificar els criteris d'acceptació rellevants i accessibilitat.\n5. Afegir CI del producte i un runbook de desplegament/restauració abans de producció.\n\n## Funcionalitats acordades\n\n" + bullets(data["mvp"]) + "\n\nNo s'han instal·lat frameworks, creat serveis ni desplegat res durant l'onboarding.\n"
    return {path: (header + body).encode() for path, body in zip(GENERATED, (brief, architecture, quality, plan))}


def initialize(root: Path, refresh: bool = False) -> dict:
    data = load_brief(root)
    output = render(root, data)
    previous = load_state(root)
    # Preflight every destination before changing any document.
    for relative, content in output.items():
        path = local(root, relative)
        if path.exists() and path.read_bytes() != content:
            old_hash = previous.get("files", {}).get(relative)
            if not refresh or old_hash != digest(path.read_bytes()):
                raise FoundationError(f"Conflicte: {relative}. Conserva i reconcilia els canvis manuals; no s'ha sobreescrit cap document.")
    state_path = local(root, "project/state.json")
    for relative, content in output.items():
        path = local(root, relative)
        if not path.exists() or path.read_bytes() != content:
            write_atomic(path, content)
    write_atomic(state_path, encoded({"schema_version": 1, "brief_sha256": digest(encoded(data)),
                                    "files": {p: digest(c) for p, c in output.items()}}))
    return status(root)


def verify_skills(root: Path) -> int:
    root = root.resolve()
    lock = read_json(local(root, "skills/lock.json"))
    files = lock.get("files", {})
    if lock.get("schema_version") != 1 or not files:
        raise FoundationError("Lock de skills absent o buit.")
    for relative, checksum in files.items():
        if not relative.startswith("vendor/"):
            raise FoundationError("El lock només pot referenciar vendor/.")
        path = local(root, relative)
        if not path.is_file() or digest(path.read_bytes()) != checksum:
            raise FoundationError(f"Integritat de skill incorrecta: {relative}")
    actual = set()
    for path in local(root, "vendor").rglob("*"):
        if path.is_symlink():
            raise FoundationError("vendor/ no pot contenir enllaços simbòlics.")
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
    if actual != set(files):
        raise FoundationError("Hi ha fitxers vendor no registrats al lock.")
    return len(files)


def validate(root: Path) -> dict:
    current = status(root)
    for profile in ("corporate", "ecommerce", "saas"):
        data = read_json(local(root, f"profiles/{profile}.json"))
        if data.get("id") != profile or not all(data.get(k) for k in ("label", "questions", "checks", "risks")):
            raise FoundationError(f"Perfil invàlid: {profile}")
    catalog = read_json(local(root, "skills/catalog.json"))
    for skill in catalog["skills"]:
        if skill["installed"]:
            if not local(root, skill["source"] + "/SKILL.md").is_file():
                raise FoundationError("Falta una skill instal·lada.")
            if skill.get("adapter") and not local(root, skill["adapter"] + "/SKILL.md").is_file():
                raise FoundationError("Falta un adaptador de skill.")
    count = verify_skills(root)
    if load_state(root) and current["phase"] != "ready":
        raise FoundationError("El brief ha canviat o falten documents. Revisa plan i init --refresh.")
    return {"valid": True, "phase": current["phase"], "vendor_files_verified": count,
            "scope": "Plantilla i onboarding; no valida la seguretat ni el funcionament del producte."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("status", "plan", "validate"):
        sub.add_parser(name)
    configure_parser = sub.add_parser("configure")
    configure_parser.add_argument("--answers", type=Path, required=True)
    init_parser = sub.add_parser("init")
    init_parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "configure":
            result = configure(ROOT, read_json(args.answers))
        elif args.command == "init":
            result = initialize(ROOT, args.refresh)
        elif args.command == "plan":
            data = load_brief(ROOT)
            result = {"status": status(ROOT), "documents": list(GENERATED), "will_install_or_deploy": False}
            if not missing(data):
                result["preview"] = {p: c.decode() for p, c in render(ROOT, data).items()}
        else:
            result = status(ROOT) if args.command == "status" else validate(ROOT)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (FoundationError, OSError, ValueError) as error:
        # JSONDecodeError messages do not contain the full input document.
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
