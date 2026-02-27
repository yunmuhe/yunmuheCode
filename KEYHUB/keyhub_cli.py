from __future__ import annotations

import argparse
import sys
import uuid
from typing import List

from keyhub_models import add_key, delete_key, get_config_path, get_current, load_config, save_config, set_current, update_key
from keyhub_export import export_current_for_codex


def _print(msg: str) -> None:
    sys.stdout.write(msg + "\n")


def cmd_list(args: argparse.Namespace) -> None:
    config = load_config()
    if not config.keys:
        _print("No keys found. Use `add` to create one.")
        return

    _print(f"Config path: {get_config_path()}")
    _print("")
    _print("ID                       Provider   Status   Name (last 4)")
    _print("-" * 64)
    for item in config.keys:
        last4 = item.key[-4:] if item.key else "????"
        line = f"{item.id:<24} {item.provider:<9} {item.status:<7} {item.name} ({last4})"
        _print(line)


def cmd_add(args: argparse.Namespace) -> None:
    config = load_config()

    key_id = args.id or str(uuid.uuid4())[:8]
    record = add_key(
        config,
        key_id=key_id,
        name=args.name or key_id,
        provider=args.provider,
        secret=args.key,
        category=args.category,
        note=args.note,
    )
    save_config(config)
    _print(f"Added key: {record.id}")


def cmd_delete(args: argparse.Namespace) -> None:
    config = load_config()
    if delete_key(config, args.id):
        save_config(config)
        _print(f"Deleted key: {args.id}")
    else:
        _print(f"Key not found: {args.id}")


def cmd_use(args: argparse.Namespace) -> None:
    config = load_config()
    set_current(config, args.cli, args.id)
    save_config(config)
    _print(f"Set current key for {args.cli!r} -> {args.id!r}")


def cmd_current(args: argparse.Namespace) -> None:
    config = load_config()
    record = get_current(config, args.cli)
    if not record:
        _print(f"No current key for CLI: {args.cli}")
        return
    last4 = record.key[-4:] if record.key else "????"
    _print(
        f"{args.cli}: {record.id} ({record.name}, last4={last4}, provider={record.provider})"
    )


def cmd_export_codex(args: argparse.Namespace) -> None:
    """Export current 'codex' key into Codex auth.json."""
    if export_current_for_codex():
        _print("Exported current 'codex' key to Codex auth.json.")
    else:
        _print("No current 'codex' key to export.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="keyhub", description="Keyhub CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List all keys")
    p_list.set_defaults(func=cmd_list)

    p_add = sub.add_parser("add", help="Add a new key")
    p_add.add_argument("--id", help="Optional custom id for the key")
    p_add.add_argument("--name", help="Human readable name")
    p_add.add_argument("--provider", default="univibe", help="Provider name")
    p_add.add_argument("--category", help="Category label, e.g. work/test")
    p_add.add_argument("--note", help="Optional note")
    p_add.add_argument("--key", required=True, help="Secret key value")
    p_add.set_defaults(func=cmd_add)

    p_del = sub.add_parser("delete", help="Delete a key by id")
    p_del.add_argument("id", help="Key id to delete")
    p_del.set_defaults(func=cmd_delete)

    p_use = sub.add_parser("use", help="Set current key for CLI")
    p_use.add_argument("cli", help="CLI name, e.g. codex/claude/gemini")
    p_use.add_argument("id", help="Key id to mark as current")
    p_use.set_defaults(func=cmd_use)

    p_cur = sub.add_parser("current", help="Show current key for CLI")
    p_cur.add_argument("cli", help="CLI name, e.g. codex/claude/gemini")
    p_cur.set_defaults(func=cmd_current)

    p_export_codex = sub.add_parser(
        "export-codex", help="Export current 'codex' key into Codex auth.json"
    )
    p_export_codex.set_defaults(func=cmd_export_codex)

    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 1
    func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
