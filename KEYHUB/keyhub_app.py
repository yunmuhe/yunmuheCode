from __future__ import annotations

import gzip
import json
import re
import urllib.request
from typing import Dict, List, Optional
from urllib.parse import urlparse

from flask import Flask, redirect, render_template, request, url_for, Response, make_response, send_file

from keyhub_models import (
    add_key,
    add_provider,
    delete_key,
    delete_provider,
    get_config_path,
    get_current,
    get_key,
    load_config,
    save_config,
    set_current,
    update_key,
    update_provider,
    KeyhubConfig,
)
from keyhub_export import (
    export_current_for_cli,
    get_claude_api_key_helper_status,
    ensure_claude_api_key_helper_configured,
    read_codex_key,
    read_claude_key,
    read_gemini_key,
)


CLI_DEFINITIONS: List[Dict[str, str]] = [
    {"id": "claude", "label": "Claude Code", "desc": "Claude 官方 AI Coding CLI"},
    {"id": "codex", "label": "Codex", "desc": "OpenAI 官方 AI Coding CLI"},
    {"id": "gemini", "label": "Gemini", "desc": "Gemini 官方 AI Coding CLI"},
]


def _safe_url_or_none(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    raw = raw.strip()
    if not raw:
        return None

    try:
        parsed = urlparse(raw)
    except Exception:
        return None

    if parsed.scheme not in {"http", "https"}:
        return None

    if not parsed.netloc:
        return None

    return raw


def _fetch_json(
    *,
    url: str,
    headers: Optional[dict] = None,
    timeout: float = 12,
) -> Optional[object]:
    try:
        req = urllib.request.Request(url, headers=headers or {})

        # Use system/environment proxies (on Windows this can pick up proxy settings).
        opener = urllib.request.build_opener(urllib.request.ProxyHandler(urllib.request.getproxies()))

        with opener.open(req, timeout=timeout) as resp:
            content_type = (resp.headers.get("content-type") or "").lower()
            encoding = (resp.headers.get("content-encoding") or "").lower()
            raw = resp.read()

        if encoding == "gzip":
            try:
                raw = gzip.decompress(raw)
            except Exception:
                return None

        # Some servers may not set content-type; be permissive.
        if "json" not in content_type and "text" not in content_type and "application" not in content_type:
            return None

        text = raw.decode("utf-8", errors="replace")
        return json.loads(text)
    except Exception:
        return None


def _extract_number_like_quota(data: object) -> Optional[str]:
    # Best-effort extraction for various possible payload shapes.
    # We only return a short string (avoid dumping huge JSON into keys.json).
    if data is None:
        return None

    candidates: List[str] = []

    def add_candidate(value: object):
        if value is None:
            return
        if isinstance(value, (int, float)):
            candidates.append(str(value))
            return
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return
            # Keep only reasonable-length values.
            if len(s) > 80:
                return
            candidates.append(s)

    if isinstance(data, dict):
        for k in [
            "quota",
            "quota_remaining",
            "remaining",
            "balance",
            "points",
            "credits",
            "credit",
            "available",
            "total",
        ]:
            if k in data:
                add_candidate(data.get(k))

        # Common nesting patterns.
        for k in ["data", "result", "payload", "account", "summary"]:
            v = data.get(k)
            if isinstance(v, dict):
                for kk, vv in v.items():
                    if kk in {"quota", "remaining", "balance", "points", "credits"}:
                        add_candidate(vv)

    if isinstance(data, list) and data:
        # Sometimes APIs return an array of balances.
        first = data[0]
        if isinstance(first, dict):
            for k in ["quota", "remaining", "balance", "points", "credits", "total"]:
                if k in first:
                    add_candidate(first.get(k))

    # If we have explicit numeric candidates, prefer numeric.
    for c in candidates:
        if re.fullmatch(r"\d+(?:\.\d+)?", c):
            return c

    return candidates[0] if candidates else None


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/assets/keyhub.css")
    def keyhub_css():
        from pathlib import Path

        css_path = Path(__file__).resolve().parent / "templates" / "keyhub.css"
        css = css_path.read_text(encoding="utf-8")
        return Response(css, mimetype="text/css")

    @app.route("/")
    def index():
        config = load_config()

        ui_active_cli = request.args.get("cli")
        if ui_active_cli not in {"codex", "claude", "gemini"}:
            ui_active_cli = None

        ui_key_id = request.args.get("key")
        ui_focus = request.args.get("focus")

        # Operational default: keep forms/export working even when UI has no selection.
        active_cli = ui_active_cli or "codex"

        current_map = {}
        for item in CLI_DEFINITIONS:
            cli_id = item["id"]
            current_map[cli_id] = get_current(config, cli_id)

        cli_with_current: List[Dict[str, object]] = []
        for item in CLI_DEFINITIONS:
            cli_id = item["id"]
            cli_with_current.append(
                {
                    "id": cli_id,
                    "label": item["label"],
                    "desc": item["desc"],
                    "current": current_map.get(cli_id),
                }
            )

        current_for_ui = current_map.get(ui_active_cli) if ui_active_cli else None
        selected_key_id = current_for_ui.id if current_for_ui else None

        # UI highlight priority:
        # - focus=key: highlight key param
        # - focus=cli: highlight APPLIED for cli (fallback SELECTED)
        # - otherwise: if key param exists highlight it; else if cli exists highlight APPLIED (fallback SELECTED)
        highlight_key_id = None

        applied_map: Dict[str, List[str]] = {}
        applied_current: Dict[str, object] = {}
        applied_suffix: Dict[str, str] = {}

        codex_key = read_codex_key()
        if codex_key:
            applied_map["codex"] = [item.id for item in config.keys if item.key == codex_key]
            applied_suffix["codex"] = codex_key[-4:]
            for item in config.keys:
                if item.key == codex_key:
                    applied_current["codex"] = item
                    break

        claude_key = read_claude_key()
        if claude_key:
            applied_map["claude"] = [item.id for item in config.keys if item.key == claude_key]
            applied_suffix["claude"] = claude_key[-4:]
            for item in config.keys:
                if item.key == claude_key:
                    applied_current["claude"] = item
                    break

        gemini_key = read_gemini_key()
        if gemini_key:
            applied_map["gemini"] = [item.id for item in config.keys if item.key == gemini_key]
            applied_suffix["gemini"] = gemini_key[-4:]
            for item in config.keys:
                if item.key == gemini_key:
                    applied_current["gemini"] = item
                    break

        claude_helper_status = get_claude_api_key_helper_status()

        def _applied_or_selected_id(cli_id: str | None) -> str | None:
            if not cli_id:
                return None
            applied_for_ui = applied_current.get(cli_id)
            if applied_for_ui is not None and getattr(applied_for_ui, "id", None):
                return getattr(applied_for_ui, "id", None)
            return selected_key_id

        if ui_focus == "key":
            highlight_key_id = ui_key_id or None
        elif ui_focus == "cli":
            highlight_key_id = _applied_or_selected_id(ui_active_cli)
        else:
            highlight_key_id = (ui_key_id or None) or _applied_or_selected_id(ui_active_cli)

        current_active_id = highlight_key_id

        return render_template(
            "index.html",
            config_path=get_config_path(),
            config=config,
            providers=config.providers,
            cli_definitions=cli_with_current,
            active_cli=active_cli,
            ui_active_cli=ui_active_cli,
            ui_key_id=ui_key_id,
            ui_focus=ui_focus,
            current_active_id=current_active_id,
            applied_map=applied_map,
            applied_current=applied_current,
            applied_suffix=applied_suffix,
            claude_helper_status=claude_helper_status,
        )

    @app.post("/add")
    def add():
        config = load_config()
        name = request.form.get("name", "").strip()
        provider = request.form.get("provider", "univibe").strip() or "univibe"
        secret = request.form.get("key", "").strip()
        category = request.form.get("category", "").strip() or None
        note = request.form.get("note", "").strip() or None
        quota_remaining = request.form.get("quota_remaining", "").strip() or None
        auth_token = request.form.get("auth_token", "").strip() or None

        active_cli = request.args.get("cli", "codex")

        if not secret:
            return redirect(url_for("index", cli=active_cli))

        add_key(
            config,
            key_id=str(len(config.keys) + 1),
            name=name or f"Key {len(config.keys) + 1}",
            provider=provider,
            secret=secret,
            category=category,
            note=note,
            quota_remaining=quota_remaining,
            auth_token=auth_token,
        )
        save_config(config)
        resp = make_response(redirect(url_for("index", cli=active_cli)))
        resp.set_cookie("kh_saved", "create_key", max_age=10, samesite="Lax")
        return resp

    @app.post("/use/<cli_name>/<key_id>")
    def use(cli_name: str, key_id: str):
        config = load_config()
        set_current(config, cli_name, key_id)
        save_config(config)
        return redirect(url_for("index", cli=cli_name, key=key_id, focus="key"))

    @app.post("/edit/<key_id>")
    def edit(key_id: str):
        config = load_config()

        name = request.form.get("name", "").strip()
        provider = request.form.get("provider", "univibe").strip() or "univibe"
        secret = request.form.get("key", "").strip()
        category = request.form.get("category", "").strip() or None
        note = request.form.get("note", "").strip() or None
        quota_remaining = request.form.get("quota_remaining", "").strip() or None
        auth_token = request.form.get("auth_token", "").strip() or None

        active_cli = request.args.get("cli", "codex")

        update_key(
            config,
            key_id,
            name=name,
            provider=provider,
            secret=secret if secret else None,
            category=category,
            note=note,
            quota_remaining=quota_remaining,
            auth_token=auth_token,
        )
        save_config(config)
        resp = make_response(redirect(url_for("index", cli=active_cli)))
        resp.set_cookie("kh_saved", "edit_key", max_age=10, samesite="Lax")
        return resp

    @app.post("/delete/<key_id>")
    def delete(key_id: str):
        config = load_config()
        active_cli = request.args.get("cli", "codex")
        delete_key(config, key_id)
        save_config(config)
        return redirect(url_for("index", cli=active_cli))

    @app.post("/providers/add")
    def add_provider_view():
        config = load_config()

        provider_id = request.form.get("provider_id", "").strip()
        name = request.form.get("name", "").strip()
        api_url = request.form.get("api_url", "").strip() or None
        website = request.form.get("website", "").strip() or None
        auth_token = request.form.get("auth_token", "").strip() or None

        active_cli = request.args.get("cli", "codex")

        models = [s.strip() for s in request.form.getlist("models") if s.strip()]
        if provider_id and name:
            add_provider(
                config,
                provider_id=provider_id,
                name=name,
                models=models,
                api_url=api_url,
                website=website,
                auth_token=auth_token,
            )
            save_config(config)
            resp = make_response(redirect(url_for("index", cli=active_cli)))
            resp.set_cookie("kh_saved", "create_provider", max_age=10, samesite="Lax")
            return resp

        return redirect(url_for("index", cli=active_cli))

    @app.post("/providers/edit/<provider_id>")
    def edit_provider_view(provider_id: str):
        config = load_config()

        name = request.form.get("name", "").strip()
        api_url = request.form.get("api_url", "").strip() or None
        website = request.form.get("website", "").strip() or None
        auth_token = request.form.get("auth_token", "").strip() or None
        models = [s.strip() for s in request.form.getlist("models") if s.strip()]

        active_cli = request.args.get("cli", "codex")

        if name:
            update_provider(
                config,
                provider_id,
                name=name,
                models=models,
                api_url=api_url,
                website=website,
                auth_token=auth_token,
            )
            save_config(config)
            resp = make_response(redirect(url_for("index", cli=active_cli)))
            resp.set_cookie("kh_saved", "edit_provider", max_age=10, samesite="Lax")
            return resp

        return redirect(url_for("index", cli=active_cli))

    @app.post("/providers/delete/<provider_id>")
    def delete_provider_view(provider_id: str):
        config = load_config()
        active_cli = request.args.get("cli", "codex")
        delete_provider(config, provider_id)
        save_config(config)
        return redirect(url_for("index", cli=active_cli))

    @app.post("/export/<cli_name>")
    def export_cli_view(cli_name: str):
        ok = export_current_for_cli(cli_name)

        if cli_name == "claude":
            try:
                ensure_claude_api_key_helper_configured()
            except Exception:
                pass

        resp = make_response(redirect(url_for("index", cli=cli_name)))
        if ok:
            resp.set_cookie("kh_saved", "export", max_age=10, samesite="Lax")
        return resp

    @app.post("/keys/<key_id>/quota/refresh")
    def refresh_key_quota_view(key_id: str):
        config = load_config()
        record = get_key(config, key_id)
        if not record:
            return redirect(url_for("index", cli=request.args.get("cli", "codex")))

        active_cli = request.args.get("cli", "codex")

        # Provider API URL is stored on provider record (optional).
        provider = None
        for p in config.providers:
            if p.id == record.provider:
                provider = p
                break

        base_url = _safe_url_or_none(getattr(provider, "api_url", None) if provider else None)

        # Default: do nothing if no provider api_url configured.
        # This keeps behavior explicit and avoids guessing endpoints.
        ok = False
        quota_value: Optional[str] = None

        endpoint: Optional[str] = None
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": "Mozilla/5.0",
        }

        # Univibe uses a session Bearer token (not the AI API key).
        # Store it on provider.auth_token to avoid mixing it into key records.
        if str(record.provider) == "univibe":
            # Prefer per-key auth token (each key is an account).
            token = (getattr(record, "auth_token", None) or "").strip()
            if not token:
                token = (getattr(provider, "auth_token", None) or "").strip() if provider else ""
            if token:
                headers["Authorization"] = f"Bearer {token}"

        # Univibe: known credits detail endpoint.
        # This matches what the web console calls on the "积分详情" page.
        if str(record.provider) == "univibe":
            endpoint = "https://www.univibe.cc/api/credits/detail"
            headers["X-Requested-With"] = "XMLHttpRequest"
        elif base_url:
            # Generic fallback: <api_url>/quota
            # User can set api_url to the exact service root they control.
            endpoint = base_url.rstrip("/") + "/quota"

        if endpoint:
            data = _fetch_json(
                url=endpoint,
                headers=headers,
                timeout=12,
            )

            # Exact extraction for univibe response shape.
            if str(record.provider) == "univibe" and isinstance(data, dict):
                credit = data.get("credit")
                if isinstance(credit, dict):
                    raw = credit.get("current_credits")
                    if isinstance(raw, (int, float)):
                        quota_value = str(raw)
                    elif isinstance(raw, str) and raw.strip():
                        quota_value = raw.strip()

            # Fallback to heuristic extractor.
            if not quota_value:
                quota_value = _extract_number_like_quota(data)

            if quota_value:
                record.quota_remaining = quota_value
                ok = True

        if ok:
            save_config(config)
            resp = make_response(redirect(url_for("index", cli=active_cli, key=key_id, focus="key")))
            resp.set_cookie("kh_saved", "refresh_quota", max_age=10, samesite="Lax")
            return resp

        # Failure: keep user on same selection, no destructive changes.
        resp = make_response(redirect(url_for("index", cli=active_cli, key=key_id, focus="key")))
        resp.set_cookie("kh_saved", "refresh_quota_failed", max_age=10, samesite="Lax")
        return resp

    @app.post("/config/import")
    def import_config_view():
        file = request.files.get("config")
        if not file:
            return redirect(url_for("index"))

        try:
            raw = file.read()
            data = json.loads(raw.decode("utf-8"))
            config = KeyhubConfig.from_dict(data)
            save_config(config)

            resp = make_response(redirect(url_for("index")))
            resp.set_cookie("kh_saved", "import_config", max_age=10, samesite="Lax")
            return resp
        except Exception:
            return redirect(url_for("index"))

    @app.get("/config/export")
    def export_config_view():
        path = get_config_path()
        if not path.exists():
            config = KeyhubConfig.empty()
            save_config(config)

        return send_file(
            str(path),
            mimetype="application/json",
            as_attachment=True,
            download_name="keys.json",
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

