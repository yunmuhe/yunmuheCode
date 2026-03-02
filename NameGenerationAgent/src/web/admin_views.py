"""
Flask admin web views.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
ADMIN_SESSION_KEY = "admin_user_id"


def _auth_service():
    import src.core.auth_service as auth_module

    return auth_module.auth_service


def _record_service():
    import src.core.record_service as record_module

    return record_module.record_service


def _current_admin_user():
    user_id = session.get(ADMIN_SESSION_KEY)
    if not user_id:
        return None
    user = _auth_service().get_user_by_id(int(user_id))
    if not user:
        session.pop(ADMIN_SESSION_KEY, None)
        return None
    if user.get("role") != "admin" or not user.get("is_enabled", False):
        session.pop(ADMIN_SESSION_KEY, None)
        return None
    return user


def admin_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        user = _current_admin_user()
        if not user:
            return redirect(url_for("admin.login", next=request.path))
        return func(*args, **kwargs)

    return wrapped


def _parse_date(value: str, end_of_day: bool = False):
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        base = datetime.strptime(raw, "%Y-%m-%d")
        if end_of_day:
            return base + timedelta(hours=23, minutes=59, seconds=59)
        return base
    except Exception:
        return None


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if _current_admin_user():
            return redirect(url_for("admin.dashboard"))
        return render_template("admin/login.html", error="")

    phone = (request.form.get("phone") or "").strip()
    password = request.form.get("password") or ""
    success, payload, _ = _auth_service().login_user(phone=phone, password=password)
    if not success:
        return render_template("admin/login.html", error=payload.get("error") or "登录失败"), 401

    user = payload.get("user") or {}
    token = payload.get("token") or ""
    if token:
        _auth_service().logout_token(token)

    if user.get("role") != "admin":
        return render_template("admin/login.html", error="仅管理员可访问后台"), 403

    session[ADMIN_SESSION_KEY] = user.get("id")
    target = request.args.get("next") or url_for("admin.dashboard")
    return redirect(target)


@admin_bp.route("/logout", methods=["POST"])
@admin_required
def logout():
    session.pop(ADMIN_SESSION_KEY, None)
    return redirect(url_for("admin.login"))


@admin_bp.route("", methods=["GET"])
@admin_bp.route("/", methods=["GET"])
@admin_required
def dashboard():
    phone = (request.args.get("phone") or "").strip()
    role = (request.args.get("role") or "").strip()
    enabled_raw = (request.args.get("enabled") or "").strip()
    enabled = None
    if enabled_raw in {"0", "1"}:
        enabled = enabled_raw == "1"

    try:
        page = int(request.args.get("page", 1))
    except Exception:
        page = 1
    try:
        page_size = int(request.args.get("page_size", 20))
    except Exception:
        page_size = 20

    users_result = _auth_service().list_users(
        phone=phone,
        role=role,
        enabled=enabled,
        page=page,
        page_size=page_size,
    )
    return render_template(
        "admin/users.html",
        admin_user=_current_admin_user(),
        result=users_result,
        filters={"phone": phone, "role": role, "enabled": enabled_raw},
    )


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@admin_required
def user_detail(user_id: int):
    user = _auth_service().get_user_by_id(user_id)
    if not user:
        abort(404)

    start_text = (request.args.get("start") or "").strip()
    end_text = (request.args.get("end") or "").strip()
    start_dt = _parse_date(start_text, end_of_day=False)
    end_dt = _parse_date(end_text, end_of_day=True)

    try:
        page = int(request.args.get("page", 1))
    except Exception:
        page = 1
    try:
        page_size = int(request.args.get("page_size", 20))
    except Exception:
        page_size = 20

    records_result = _record_service().list_records_for_admin(
        user_id=user_id,
        start=start_dt,
        end=end_dt,
        page=page,
        page_size=page_size,
    )

    return render_template(
        "admin/user_detail.html",
        admin_user=_current_admin_user(),
        user=user,
        records_result=records_result,
        filters={"start": start_text, "end": end_text},
    )


@admin_bp.route("/users/<int:user_id>/enable", methods=["POST"])
@admin_required
def enable_user(user_id: int):
    _auth_service().set_user_enabled(user_id, True)
    return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/disable", methods=["POST"])
@admin_required
def disable_user(user_id: int):
    _auth_service().set_user_enabled(user_id, False)
    return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@admin_required
def reset_user_password(user_id: int):
    _auth_service().reset_user_password(user_id, temp_password="123456")
    return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/records/<int:record_id>/delete", methods=["POST"])
@admin_required
def delete_record(record_id: int):
    user_id = int(request.form.get("user_id") or 0)
    _record_service().delete_record(record_id)
    if user_id > 0:
        return redirect(url_for("admin.user_detail", user_id=user_id))
    return redirect(url_for("admin.dashboard"))
