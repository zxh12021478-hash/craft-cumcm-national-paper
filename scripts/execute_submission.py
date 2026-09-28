#!/usr/bin/env python3
"""Execute a modeling code bundle in an isolated copy and record reproducibility evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import venv
from pathlib import Path

ENTRY_CANDIDATES = (
    "run_all.py",
    "main.py",
    "main.m",
    "run_all.m",
    "main.R",
    "main.r",
    "main.jl",
    "main.ipynb",
)
IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    ".codex-run-venv",
    ".uv-cache",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}
SECRET_PATTERN = re.compile(r"(TOKEN|SECRET|PASSWORD|API[_-]?KEY|PRIVATE[_-]?KEY)", re.I)


def finding(severity: str, code: str, message: str, evidence=None) -> dict:
    item = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_snapshot(root: Path) -> dict[str, dict]:
    snapshot = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in IGNORED_DIRS for part in path.relative_to(root).parts):
            continue
        rel = str(path.relative_to(root))
        try:
            stat = path.stat()
            snapshot[rel] = {"bytes": stat.st_size, "sha256": sha256(path), "mtime_ns": stat.st_mtime_ns}
        except OSError:
            continue
    return snapshot


def copy_bundle(source: Path, destination: Path) -> None:
    def ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in IGNORED_DIRS}

    shutil.copytree(source, destination, ignore=ignore)


def resolve_entry(root: Path, requested: str | None) -> Path:
    if requested:
        candidate = (root / requested).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError as exc:
            raise ValueError("entry point must remain inside the copied bundle") from exc
        if not candidate.is_file():
            raise FileNotFoundError(f"entry point not found: {requested}")
        return candidate
    for name in ENTRY_CANDIDATES:
        matches = sorted(root.rglob(name))
        if matches:
            return matches[0]
    raise FileNotFoundError(f"no entry point found; expected one of {', '.join(ENTRY_CANDIDATES)}")


def inside(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    path.relative_to(root.resolve())
    return path


def schema_findings(payload: dict, schema_path: Path) -> list[dict]:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return [finding("Major", "JSONSCHEMA_UNAVAILABLE", "Execution manifest was not checked with JSON Schema.")]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    output = []
    for error in sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload), key=lambda item: list(item.absolute_path)):
        location = "/".join(str(part) for part in error.absolute_path) or "$"
        output.append(finding("Blocker", "MANIFEST_SCHEMA", f"{location}: {error.message}"))
    return output


def resolve_dependency(root: Path, requested: str | None) -> Path | None:
    if requested:
        candidate = inside(root, requested)
        if not candidate.is_file():
            raise FileNotFoundError(requested)
        return candidate
    for name in ("requirements.txt", "pyproject.toml"):
        matches = sorted(
            path for path in root.rglob(name)
            if not any(part in IGNORED_DIRS for part in path.relative_to(root).parts)
        )
        if matches:
            return matches[0]
    return None


def prepare_python(
    root: Path,
    install_deps: bool,
    mode: str,
    dependency_file: str | None,
    findings: list[dict],
) -> tuple[list[str], dict]:
    metadata = {"requested_mode": mode, "selected_mode": "system", "dependency_file": dependency_file}
    if not install_deps or mode == "system":
        return [sys.executable], metadata
    dependency = resolve_dependency(root, dependency_file)
    uv_lock = root / "uv.lock"
    uv = shutil.which("uv")
    wants_uv = mode == "uv" or (mode == "auto" and uv_lock.is_file())
    if wants_uv and uv and (root / "pyproject.toml").is_file() and uv_lock.is_file():
        command = [uv, "sync", "--frozen", "--no-progress"]
        proc = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=900)
        metadata.update(selected_mode="uv", dependency_file="uv.lock", setup_command=command)
        if proc.returncode:
            findings.append(
                finding(
                    "Critical",
                    "UV_SYNC",
                    "uv could not reproduce the locked Python environment.",
                    {"returncode": proc.returncode, "stderr_tail": proc.stderr[-6000:]},
                )
            )
        return [uv, "run", "--frozen", "python"], metadata
    if mode == "uv":
        findings.append(
            finding(
                "Critical",
                "UV_UNAVAILABLE",
                "The manifest requires uv with pyproject.toml and uv.lock, but that locked setup is unavailable.",
            )
        )
        return [sys.executable], metadata
    if wants_uv and not uv:
        findings.append(
            finding(
                "Major",
                "UV_FALLBACK",
                "uv.lock was found but uv is unavailable; falling back to a disposable venv.",
            )
        )
    env_dir = root / ".codex-run-venv"
    venv.EnvBuilder(with_pip=True, clear=True).create(env_dir)
    python = env_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    metadata["selected_mode"] = "venv"
    if dependency is None:
        findings.append(
            finding(
                "Major",
                "NO_INSTALL_SPEC",
                "Dependency installation was requested, but no requirements.txt or pyproject.toml was found.",
            )
        )
        return [str(python)], metadata
    metadata["dependency_file"] = str(dependency.relative_to(root))
    if dependency.name == "requirements.txt":
        command = [str(python), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(dependency)]
    else:
        command = [str(python), "-m", "pip", "install", "--disable-pip-version-check", str(root)]
    proc = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=900)
    metadata["setup_command"] = command
    if proc.returncode:
        findings.append(
            finding(
                "Critical",
                "DEPENDENCY_INSTALL",
                "Dependency installation failed.",
                {"command": command, "returncode": proc.returncode, "stderr_tail": proc.stderr[-6000:]},
            )
        )
    return [str(python)], metadata


def auto_command(entry: Path, root: Path, python_prefix: list[str]) -> list[str]:
    suffix = entry.suffix.lower()
    rel = entry.relative_to(root)
    if suffix == ".py":
        return [*python_prefix, str(rel)]
    if suffix == ".m":
        matlab = shutil.which("matlab")
        if matlab:
            escaped = str(rel).replace("'", "''")
            return [matlab, "-batch", f"run('{escaped}')"]
        octave = shutil.which("octave")
        if octave:
            escaped = str(rel).replace("'", "''")
            return [octave, "--quiet", "--eval", f"run('{escaped}')"]
        raise RuntimeError("MATLAB/Octave entry point found, but neither matlab nor octave is available")
    if suffix == ".r":
        rscript = shutil.which("Rscript")
        if not rscript:
            raise RuntimeError("R entry point found, but Rscript is unavailable")
        return [rscript, str(rel)]
    if suffix == ".jl":
        julia = shutil.which("julia")
        if not julia:
            raise RuntimeError("Julia entry point found, but julia is unavailable")
        return [julia, str(rel)]
    if suffix == ".ipynb":
        jupyter = shutil.which("jupyter")
        if not jupyter:
            raise RuntimeError("Notebook entry point found, but jupyter is unavailable")
        return [jupyter, "nbconvert", "--execute", "--inplace", "--to", "notebook", str(rel)]
    raise RuntimeError(f"unsupported entry-point suffix: {entry.suffix}")


def expand_argv(
    raw: list[str],
    workspace: Path,
    entry: Path | None,
    python_prefix: list[str],
) -> list[str]:
    expanded: list[str] = []
    for token in raw:
        if token == "{python}":
            expanded.extend(python_prefix)
            continue
        value = token.replace("{root}", str(workspace))
        if "{entry}" in value:
            if entry is None:
                raise ValueError("command uses {entry}, but no entry point was resolved")
            value = value.replace("{entry}", str(entry.relative_to(workspace)))
        expanded.append(value)
    return expanded


def run_verifications(
    verifications: list[dict],
    workspace: Path,
    entry: Path | None,
    python_prefix: list[str],
    env: dict[str, str],
    default_timeout: int,
    findings: list[dict],
) -> list[dict]:
    reports = []
    for verification in verifications:
        check_id = str(verification.get("id", "?"))
        required = bool(verification.get("required", True))
        try:
            inputs = [str(value) for value in verification.get("inputs", [])]
            missing_inputs = []
            for raw_input in inputs:
                try:
                    if not inside(workspace, raw_input).exists():
                        missing_inputs.append(raw_input)
                except Exception:
                    missing_inputs.append(raw_input)
            if missing_inputs:
                findings.append(
                    finding(
                        "Critical",
                        "VERIFICATION_INPUT_MISSING",
                        f"Verification {check_id} declares missing or unsafe inputs.",
                        missing_inputs,
                    )
                )
            result_only = inputs and all(
                Path(value).parts and Path(value).parts[0].lower() in {"result", "results", "output", "outputs"}
                for value in inputs
            )
            if (
                required
                and verification.get("verification_type") in {"independent_implementation", "recomputation"}
                and result_only
            ):
                findings.append(
                    finding(
                        "Critical",
                        "WEAK_VERIFICATION_INDEPENDENCE",
                        f"Verification {check_id} only declares generated outputs as inputs; add raw inputs, an approved specification, invariant, or independent derivation.",
                        inputs,
                    )
                )
            reviewer = str(verification.get("reviewed_by", ""))
            if re.search(r"ChatGPT|DeepSeek|Claude|Gemini|Codex|OpenAI|AI", reviewer, re.I):
                findings.append(
                    finding(
                        "Critical",
                        "NON_HUMAN_VERIFICATION_REVIEWER",
                        f"Verification {check_id} must be reviewed by a team member.",
                        reviewer,
                    )
                )
            command = expand_argv(verification["command_argv"], workspace, entry, python_prefix)
            if entry is not None and any(Path(token).name == entry.name for token in command[1:]):
                findings.append(
                    finding(
                        "Critical",
                        "VERIFICATION_REUSES_ENTRY",
                        f"Verification {check_id} invokes the primary entry point instead of a separate check.",
                        command,
                    )
                )
            proc = subprocess.run(
                command,
                cwd=workspace,
                env=env,
                capture_output=True,
                text=True,
                timeout=int(verification.get("timeout_seconds", default_timeout)),
            )
            combined = proc.stdout + "\n" + proc.stderr
            pass_match = bool(re.search(verification["pass_regex"], combined, re.I | re.M))
            fail_match = bool(
                verification.get("fail_regex")
                and re.search(verification["fail_regex"], combined, re.I | re.M)
            )
            passed = proc.returncode == 0 and pass_match and not fail_match
            evidence = {
                "id": check_id,
                "command": command,
                "returncode": proc.returncode,
                "pass_match": pass_match,
                "fail_match": fail_match,
                "stdout_tail": proc.stdout[-6000:],
                "stderr_tail": proc.stderr[-6000:],
            }
            reports.append({**evidence, "required": required, "passed": passed})
            if required and not passed:
                findings.append(
                    finding(
                        "Critical",
                        "VERIFICATION_FAILED",
                        f"Required independent verification failed: {check_id}.",
                        evidence,
                    )
                )
        except Exception as exc:
            evidence = {"id": check_id, "required": required, "error": str(exc)}
            reports.append({**evidence, "passed": False})
            if required:
                findings.append(
                    finding(
                        "Critical",
                        "VERIFICATION_ERROR",
                        f"Could not run required verification: {check_id}.",
                        evidence,
                    )
                )
    return reports


def sanitized_environment(inherit_secrets: bool) -> tuple[dict[str, str], list[str]]:
    env = dict(os.environ)
    removed = []
    for key in list(env):
        if key == "PYTHONPATH" or (not inherit_secrets and SECRET_PATTERN.search(key)):
            removed.append(key)
            env.pop(key, None)
    env.update(
        {
            "PYTHONHASHSEED": "0",
            "MPLBACKEND": "Agg",
            "OMP_NUM_THREADS": env.get("OMP_NUM_THREADS", "1"),
            "OPENBLAS_NUM_THREADS": env.get("OPENBLAS_NUM_THREADS", "1"),
        }
    )
    return env, sorted(removed)


def export_workspace(workspace: Path, target: Path) -> None:
    if target.exists() and any(target.iterdir()):
        raise FileExistsError(f"export directory must be absent or empty: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.rmdir()
    shutil.copytree(workspace, target)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="Submission/code-bundle directory")
    parser.add_argument("--manifest", type=Path, help="Execution manifest JSON; CLI values override it")
    parser.add_argument("--entry", help="Entry point relative to root; auto-detected when omitted")
    parser.add_argument("--command-json", help="Explicit argv JSON list; avoids shell interpretation")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--install-deps", action="store_true", help="Create a temporary Python venv and install declared dependencies")
    parser.add_argument("--python-env", choices=("auto", "venv", "uv", "system"), default=None)
    parser.add_argument("--expect", action="append", default=[], help="Required output glob, repeatable")
    parser.add_argument("--export-dir", type=Path, help="Copy the isolated workspace after execution; target must be empty or absent")
    parser.add_argument("--inherit-secrets", action="store_true", help="Allow credential-like environment variables in the child process")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    findings: list[dict] = []
    if not root.is_dir():
        report = {"root": str(root), "findings": [finding("Blocker", "ROOT", "Code-bundle directory not found.")]}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    manifest: dict = {}
    if args.manifest:
        try:
            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
            schema = Path(__file__).resolve().parent.parent / "assets" / "schemas" / "execution-manifest.schema.json"
            findings.extend(schema_findings(manifest, schema))
        except Exception as exc:
            findings.append(finding("Blocker", "MANIFEST_READ", str(exc)))
    entry_requested = args.entry or manifest.get("entry")
    timeout = args.timeout if args.timeout != 1800 or not manifest else int(manifest.get("timeout_seconds", 1800))
    expected = list(manifest.get("expected_outputs", [])) + list(args.expect)
    python_mode = args.python_env or manifest.get("python_environment", "auto")
    install_deps = args.install_deps
    raw_command = None
    if args.command_json:
        try:
            raw_command = json.loads(args.command_json)
        except json.JSONDecodeError as exc:
            findings.append(finding("Blocker", "COMMAND_JSON", str(exc)))
    elif manifest.get("command_argv"):
        raw_command = manifest["command_argv"]

    with tempfile.TemporaryDirectory(prefix="cumcm-clean-run-") as temp:
        workspace = (Path(temp) / "submission").resolve()
        copy_bundle(root, workspace)
        before = file_snapshot(workspace)
        entry: Path | None = None
        command: list[str] = []
        start = time.monotonic()
        returncode = None
        stdout = ""
        stderr = ""
        timed_out = False
        removed_env: list[str] = []
        python_metadata: dict = {}
        verification_reports: list[dict] = []
        try:
            if entry_requested or raw_command is None or any("{entry}" in token for token in (raw_command or [])):
                entry = resolve_entry(workspace, entry_requested)
            python_prefix, python_metadata = prepare_python(
                workspace,
                install_deps,
                python_mode,
                manifest.get("dependency_file"),
                findings,
            )
            if raw_command is not None:
                if not isinstance(raw_command, list) or not raw_command or not all(isinstance(x, str) for x in raw_command):
                    raise ValueError("--command-json must be a nonempty JSON array of strings")
                command = expand_argv(raw_command, workspace, entry, python_prefix)
            else:
                if entry is None:
                    raise ValueError("no entry point was resolved")
                command = auto_command(entry, workspace, python_prefix)
            env, removed_env = sanitized_environment(args.inherit_secrets)
            proc = subprocess.run(command, cwd=workspace, env=env, capture_output=True, text=True, timeout=timeout)
            returncode = proc.returncode
            stdout, stderr = proc.stdout, proc.stderr
            if returncode:
                findings.append(
                    finding(
                        "Blocker",
                        "EXECUTION_FAILED",
                        "The clean-run entry point returned a nonzero status.",
                        {"returncode": returncode, "stderr_tail": stderr[-8000:]},
                    )
                )
            raw_verifications = manifest.get("verifications", [])
            if not isinstance(raw_verifications, list):
                findings.append(finding("Blocker", "VERIFICATION_SCHEMA", "verifications must be an array."))
                raw_verifications = []
            valid_verifications = [item for item in raw_verifications if isinstance(item, dict)]
            if len(valid_verifications) != len(raw_verifications):
                findings.append(finding("Blocker", "VERIFICATION_SCHEMA", "Every verification must be an object."))
            if not any(item.get("required") is True for item in valid_verifications):
                findings.append(
                    finding(
                        "Critical",
                        "NO_REQUIRED_VERIFICATION",
                        "At least one independent verification must be required.",
                    )
                )
            verification_reports = run_verifications(
                valid_verifications,
                workspace,
                entry,
                python_prefix,
                env,
                timeout,
                findings,
            )
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            findings.append(finding("Blocker", "TIMEOUT", f"Execution exceeded {timeout} seconds."))
        except Exception as exc:
            findings.append(finding("Blocker", "EXECUTOR", str(exc)))

        elapsed = round(time.monotonic() - start, 3)
        after = file_snapshot(workspace)
        created = sorted(set(after) - set(before))
        modified = sorted(path for path in set(after) & set(before) if after[path] != before[path])
        missing_expected = []
        stale_expected = []
        changed_paths = set(created) | set(modified)
        for pattern in expected:
            matches = list(workspace.glob(pattern))
            if not matches:
                matches = list(workspace.rglob(pattern))
            if not matches:
                missing_expected.append(pattern)
            elif not any(
                str(path.relative_to(workspace)) in changed_paths
                for path in matches
                if path.is_file()
            ):
                stale_expected.append(pattern)
        if missing_expected:
            findings.append(finding("Critical", "MISSING_EXPECTED_OUTPUT", "Required output patterns were not produced.", missing_expected))
        if stale_expected:
            findings.append(
                finding(
                    "Critical",
                    "EXPECTED_NOT_REGENERATED",
                    "Expected outputs existed but were not created or modified by this run.",
                    stale_expected,
                )
            )

        if args.export_dir:
            try:
                export_workspace(workspace, args.export_dir.resolve())
            except Exception as exc:
                findings.append(finding("Critical", "EXPORT", str(exc)))

        report = {
            "root": str(root),
            "entry": str(entry.relative_to(workspace)) if entry else None,
            "command": command,
            "manifest": str(args.manifest.resolve()) if args.manifest else None,
            "python_environment": python_metadata,
            "returncode": returncode,
            "timed_out": timed_out,
            "elapsed_seconds": elapsed,
            "environment_variables_removed": removed_env,
            "isolation_notice": "Copied working directory and sanitized environment only; not an OS security sandbox.",
            "created_files": created,
            "modified_files": modified,
            "stdout_tail": stdout[-12000:],
            "stderr_tail": stderr[-12000:],
            "verifications": verification_reports,
            "findings": findings,
        }

    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    severities = {item["severity"] for item in findings}
    return int(bool({"Blocker", "Critical"} & severities))


if __name__ == "__main__":
    raise SystemExit(main())
