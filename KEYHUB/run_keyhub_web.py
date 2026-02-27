from __future__ import annotations

import argparse
import atexit
import os
import sys
from pathlib import Path


def _add_keyhub_to_syspath() -> Path:
    keyhub_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(keyhub_dir))
    return keyhub_dir


def _write_pid_file(pid_file: Path) -> None:
    pid_file.write_text(str(os.getpid()), encoding="utf-8")


def _cleanup_pid_file(pid_file: Path) -> None:
    try:
        if not pid_file.exists():
            return
        content = pid_file.read_text(encoding="utf-8").strip()
        if content == str(os.getpid()):
            pid_file.unlink(missing_ok=True)
    except Exception:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Run KEYHUB Flask Web UI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    keyhub_dir = _add_keyhub_to_syspath()
    try:
        from keyhub_app import create_app
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            f"Failed to import KEYHUB app from {keyhub_dir}. "
            "Make sure you are running this script from the repository checkout."
        ) from exc

    pid_file = keyhub_dir / ".keyhub.pid"
    _write_pid_file(pid_file)
    atexit.register(lambda: _cleanup_pid_file(pid_file))

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=False)


if __name__ == "__main__":
    main()
