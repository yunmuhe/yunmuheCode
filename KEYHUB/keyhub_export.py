from __future__ import annotations

import base64
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional

from keyhub_models import KeyhubConfig, get_current, load_config


CLAUDE_BASE_URL_DEFAULT = "https://api.univibe.cc/anthropic"
CLAUDE_SETTINGS_SCHEMA = "https://json.schemastore.org/claude-code-settings.json"


def get_claude_settings_path() -> Path:
    return Path.home() / ".claude" / "settings.json"


def get_keyhub_api_key_helper_path() -> Path:
    return Path.home() / ".claude" / "keyhub_api_key_helper.py"


def _expected_api_key_helper_command() -> str:
    python_path = Path(sys.executable).as_posix()
    script_path = get_keyhub_api_key_helper_path().as_posix()
    return f'"{python_path}" "{script_path}"'


_KEYHUB_API_KEY_HELPER_CONTENT = """#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Iterable, Optional


def _candidate_config_paths() -> Iterable[Path]:
    env_path = (os.environ.get(\"KEYHUB_CONFIG\") or \"\").strip()
    if env_path:
        yield Path(env_path)

    yield Path.home() / \"keys.json\"
    yield Path.home() / \".claude\" / \"keys.json\"
    yield Path.home() / \"CCC\" / \"projects\" / \"KEYHUB\" / \"keys.json\"


def _load_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding=\"utf-8\"))
    except Exception:
        return None


def _get_key_from_keyhub_config(data: dict) -> Optional[str]:
    current_id = (data.get(\"current\") or {}).get(\"claude\")
    if not current_id:
        return None

    for item in data.get(\"keys\") or []:
        if str(item.get(\"id\")) == str(current_id):
            key = (item.get(\"key\") or \"\").strip()
            return key or None

    return None


def main() -> int:
    for config_path in _candidate_config_paths():
        if not config_path.exists():
            continue
        data = _load_json(config_path)
        if not isinstance(data, dict):
            continue
        key = _get_key_from_keyhub_config(data)
        if key:
            sys.stdout.write(key)
            return 0

    fallback = (os.environ.get(\"ANTHROPIC_AUTH_TOKEN\") or \"\").strip()
    if fallback:
        sys.stdout.write(fallback)
        return 0

    debug = (os.environ.get(\"KEYHUB_HELPER_DEBUG\") or \"\").strip().lower() in {\"1\", \"true\", \"yes\"}
    if debug:
        checked = \", \".join(str(p) for p in _candidate_config_paths())
        print(f\"No key found. Checked: {checked}\", file=sys.stderr)
        print(\"No ANTHROPIC_AUTH_TOKEN in process env for fallback.\", file=sys.stderr)

    return 1


if __name__ == \"__main__\":
    raise SystemExit(main())
"""


def get_claude_api_key_helper_status() -> dict:
    settings_path = get_claude_settings_path()
    helper_path = get_keyhub_api_key_helper_path()
    expected = _expected_api_key_helper_command()

    current = None
    if settings_path.exists():
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                current = data.get("apiKeyHelper")
        except Exception:
            current = None

    configured = (
        isinstance(current, str)
        and current.strip() == expected
        and helper_path.exists()
    )

    return {
        "configured": configured,
        "settings_path": str(settings_path),
        "helper_path": str(helper_path),
        "expected": expected,
        "current": current,
    }


def ensure_claude_api_key_helper_configured() -> bool:
    helper_path = get_keyhub_api_key_helper_path()
    helper_path.parent.mkdir(parents=True, exist_ok=True)

    if not helper_path.exists():
        helper_path.write_text(_KEYHUB_API_KEY_HELPER_CONTENT, encoding="utf-8")

    settings_path = get_claude_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    data: dict = {}
    if settings_path.exists():
        try:
            loaded = json.loads(settings_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            data = {}

    data.setdefault("$schema", CLAUDE_SETTINGS_SCHEMA)
    data["apiKeyHelper"] = _expected_api_key_helper_command()

    settings_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def _detect_shell_profile_path() -> Path:
    shell = (os.environ.get("SHELL") or "").lower()
    if shell.endswith("zsh") or shell.endswith("/zsh"):
        return Path.home() / ".zshrc"
    if shell.endswith("bash") or shell.endswith("/bash"):
        return Path.home() / ".bash_profile"
    # macOS default shell is zsh; using .zshrc as a reasonable fallback.
    return Path.home() / ".zshrc"


def _shell_escape_double_quotes(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _upsert_export_line(profile: Path, var_name: str, value: str) -> None:
    profile.parent.mkdir(parents=True, exist_ok=True)
    if not profile.exists():
        profile.write_text("", encoding="utf-8")

    raw = profile.read_text(encoding="utf-8")
    lines = raw.splitlines(True)
    export_re = re.compile(r"^\s*export\s+" + re.escape(var_name) + r"=", re.IGNORECASE)

    new_line = f'export {var_name}="{_shell_escape_double_quotes(value)}"\n'

    replaced = False
    for idx, line in enumerate(lines):
        if export_re.match(line):
            lines[idx] = new_line
            replaced = True
            break

    if not replaced:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] = lines[-1] + "\n"
        lines.append(new_line)

    profile.write_text("".join(lines), encoding="utf-8")


def _read_exported_var_from_profile(profile: Path, var_name: str) -> Optional[str]:
    if not profile.exists():
        return None

    export_re = re.compile(
        r"^\s*export\s+" + re.escape(var_name) + r"\s*=\s*(.+?)\s*$",
        re.IGNORECASE,
    )

    try:
        lines = profile.read_text(encoding="utf-8").splitlines()
    except Exception:
        return None

    for line in reversed(lines):
        m = export_re.match(line)
        if not m:
            continue
        value = m.group(1).strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        value = value.strip()
        return value or None

    return None


def get_codex_auth_path() -> Path:
    """Return the path to Codex auth.json file."""
    return Path.home() / ".codex" / "auth.json"


def read_codex_key(path: Optional[Path] = None) -> Optional[str]:
    """Read Codex OPENAI_API_KEY from auth.json, if present."""
    target = path or get_codex_auth_path()
    if not target.exists():
        return None

    try:
        with target.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None

    value = data.get("OPENAI_API_KEY")
    return value if isinstance(value, str) and value.strip() else None


def write_codex_key(secret: str, path: Optional[Path] = None) -> None:
    """Write the given key into Codex auth.json as OPENAI_API_KEY."""
    target = path or get_codex_auth_path()
    target.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    if target.exists():
        try:
            with target.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    data["OPENAI_API_KEY"] = secret

    with target.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def read_claude_key() -> Optional[str]:
    """Read ANTHROPIC_AUTH_TOKEN.

    - Windows: user-level environment variable
    - macOS/Linux: prefer current env, fallback to shell profile export
    """
    if sys.platform != "win32":
        value = os.environ.get("ANTHROPIC_AUTH_TOKEN", "").strip()
        if value:
            return value
        profile = _detect_shell_profile_path()
        return _read_exported_var_from_profile(profile, "ANTHROPIC_AUTH_TOKEN")

    # Fast path: read from registry (user-level env vars).
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_READ,
        ) as key:
            value, _ = winreg.QueryValueEx(key, "ANTHROPIC_AUTH_TOKEN")
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return None
    except Exception:
        return None


def write_claude_key(secret: str, base_url: str = CLAUDE_BASE_URL_DEFAULT) -> None:
    """Persist Claude Code env.

    - Windows: user-level env vars via registry/PowerShell
    - macOS/Linux: write to shell profile (zshrc/bash_profile)
    """
    if sys.platform != "win32":
        profile = _detect_shell_profile_path()
        _upsert_export_line(profile, "ANTHROPIC_BASE_URL", base_url)
        _upsert_export_line(profile, "ANTHROPIC_AUTH_TOKEN", secret)
        os.environ["ANTHROPIC_BASE_URL"] = base_url
        os.environ["ANTHROPIC_AUTH_TOKEN"] = secret
        return

    import subprocess

    # Prefer Windows registry write (silent, no console popups).
    # Fallback to PowerShell if registry write fails.
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(key, "ANTHROPIC_BASE_URL", 0, winreg.REG_SZ, base_url)
            winreg.SetValueEx(key, "ANTHROPIC_AUTH_TOKEN", 0, winreg.REG_SZ, secret)
        return
    except Exception:
        pass

    # PowerShell fallback: run via encoded command to avoid quoting issues.
    script = (
        '[System.Environment]::SetEnvironmentVariable('
        '"ANTHROPIC_BASE_URL", '
        f'"{base_url}", '
        '[System.EnvironmentVariableTarget]::User); '
        '[System.Environment]::SetEnvironmentVariable('
        '"ANTHROPIC_AUTH_TOKEN", '
        f'"{secret}", '
        '[System.EnvironmentVariableTarget]::User)'
    )
    encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")

    powershell = shutil.which("pwsh") or shutil.which("powershell")
    if not powershell:
        raise RuntimeError("PowerShell not found. Please install PowerShell or ensure it is on PATH.")

    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0

    subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
        check=True,
        capture_output=True,
        startupinfo=startupinfo,
        creationflags=(0x08000000 if sys.platform == "win32" else 0),
    )


def read_gemini_key() -> Optional[str]:
    """Read GEMINI_API_KEY.

    - Windows: user-level environment variable
    - macOS/Linux: prefer current env, fallback to shell profile export
    """
    if sys.platform != "win32":
        value = os.environ.get("GEMINI_API_KEY", "").strip()
        if value:
            return value
        profile = _detect_shell_profile_path()
        return _read_exported_var_from_profile(profile, "GEMINI_API_KEY")

    # Fast path: read from registry (user-level env vars).
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_READ,
        ) as key:
            value, _ = winreg.QueryValueEx(key, "GEMINI_API_KEY")
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return None
    except Exception:
        return None


def _write_user_env_var_windows(name: str, value: str) -> None:
    """Write a user-level environment variable on Windows."""
    import winreg

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Environment",
        0,
        winreg.KEY_SET_VALUE,
    ) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)


def write_gemini_env(secret: str, base_url: str = "https://api.univibe.cc/gemini") -> None:
    """Persist Gemini CLI env.

    - Windows: user-level env vars via registry (fallback PowerShell)
    - macOS/Linux: write to shell profile (zshrc/bash_profile)
    """
    if sys.platform != "win32":
        profile = _detect_shell_profile_path()
        _upsert_export_line(profile, "GOOGLE_GEMINI_BASE_URL", base_url)
        _upsert_export_line(profile, "GEMINI_API_KEY", secret)
        os.environ["GOOGLE_GEMINI_BASE_URL"] = base_url
        os.environ["GEMINI_API_KEY"] = secret
        return

    # Prefer registry write (silent). Fallback to PowerShell if needed.
    try:
        _write_user_env_var_windows("GOOGLE_GEMINI_BASE_URL", base_url)
        _write_user_env_var_windows("GEMINI_API_KEY", secret)
        return
    except Exception:
        pass

    import subprocess

    script = (
        '[System.Environment]::SetEnvironmentVariable('
        '"GOOGLE_GEMINI_BASE_URL", '
        f'"{base_url}", '
        '[System.EnvironmentVariableTarget]::User); '
        '[System.Environment]::SetEnvironmentVariable('
        '"GEMINI_API_KEY", '
        f'"{secret}", '
        '[System.EnvironmentVariableTarget]::User)'
    )
    encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")

    powershell = shutil.which("pwsh") or shutil.which("powershell")
    if not powershell:
        raise RuntimeError("PowerShell not found. Please install PowerShell or ensure it is on PATH.")

    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0

    subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
        check=True,
        capture_output=True,
        startupinfo=startupinfo,
        creationflags=(0x08000000 if sys.platform == "win32" else 0),
    )


def export_current_for_codex(config: Optional[KeyhubConfig] = None) -> bool:
    cfg = config or load_config()
    record = get_current(cfg, "codex")
    if not record or not record.key:
        return False
    write_codex_key(record.key)
    return True


def export_current_for_claude(config: Optional[KeyhubConfig] = None) -> bool:
    cfg = config or load_config()
    record = get_current(cfg, "claude")
    if not record or not record.key:
        return False
    write_claude_key(record.key)
    return True


def export_current_for_gemini(config: Optional[KeyhubConfig] = None) -> bool:
    cfg = config or load_config()
    record = get_current(cfg, "gemini")
    if not record or not record.key:
        return False
    write_gemini_env(record.key)
    return True


def export_current_for_cli(cli_name: str, config: Optional[KeyhubConfig] = None) -> bool:
    if cli_name == "codex":
        return export_current_for_codex(config)
    if cli_name == "claude":
        return export_current_for_claude(config)
    if cli_name == "gemini":
        return export_current_for_gemini(config)
    return False

