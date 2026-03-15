"""Helpers for configuring the Flask development server."""

from __future__ import annotations

import sys


def get_dev_server_options(debug: bool, platform: str | None = None) -> dict[str, object]:
    """Return app.run options that avoid Windows reloader socket errors."""
    current_platform = platform or sys.platform
    options: dict[str, object] = {"debug": debug}
    if debug and current_platform == "win32":
        options["use_reloader"] = False
    return options
