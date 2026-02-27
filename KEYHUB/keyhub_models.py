from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


CONFIG_FILENAME = "keys.json"


def get_config_path() -> Path:
    """Return the path to the keys.json file under the user's home directory."""
    return Path.home() / CONFIG_FILENAME


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class KeyRecord:
    id: str
    name: str
    provider: str
    cli_targets: List[str]
    key: str
    category: Optional[str] = None
    note: Optional[str] = None
    quota_remaining: Optional[str] = None
    auth_token: Optional[str] = None
    status: str = "active"
    created_at: str = field(default_factory=_now_iso_utc)
    last_used_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "KeyRecord":
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            provider=(
                "univibe"
                if str(data.get("provider", "univibe") or "univibe").strip().lower() == "univivbe"
                else str(data.get("provider", "univibe") or "univibe").strip().lower()
            ),
            cli_targets=list(data.get("cli_targets", [])),
            key=data["key"],
            category=data.get("category"),
            note=data.get("note"),
            quota_remaining=data.get("quota_remaining"),
            auth_token=data.get("auth_token"),
            status=data.get("status", "active"),
            created_at=data.get("created_at", _now_iso_utc()),
            last_used_at=data.get("last_used_at"),
        )

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ProviderRecord:
    id: str
    name: str
    models: List[str]
    api_url: Optional[str] = None
    website: Optional[str] = None
    auth_token: Optional[str] = None
    created_at: str = field(default_factory=_now_iso_utc)

    @classmethod
    def from_dict(cls, data: Dict) -> "ProviderRecord":
        return cls(
            id=(
                "univibe"
                if str(data["id"]).strip().lower() == "univivbe"
                else str(data["id"]).strip().lower()
            ),
            name=data.get("name", data["id"]),
            models=["openai" if m == "codex" else m for m in list(data.get("models", []))],
            api_url=data.get("api_url"),
            website=data.get("website") or data.get("homepage"),
            auth_token=data.get("auth_token"),
            created_at=data.get("created_at", _now_iso_utc()),
        )

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class KeyhubConfig:
    version: int = 1
    current: Dict[str, Optional[str]] = field(default_factory=dict)
    keys: List[KeyRecord] = field(default_factory=list)
    providers: List[ProviderRecord] = field(default_factory=list)

    @classmethod
    def empty(cls) -> "KeyhubConfig":
        return cls(
            version=1,
            current={"codex": None, "claude": None, "gemini": None},
            keys=[],
            providers=[
                ProviderRecord(id="univibe", name="Univibe", models=["openai", "claude", "gemini"], api_url=None)
            ],
        )

    @classmethod
    def from_dict(cls, data: Dict) -> "KeyhubConfig":
        keys_data = data.get("keys", [])
        keys = [KeyRecord.from_dict(item) for item in keys_data]

        providers_data = data.get("providers")
        if providers_data is None:
            providers = [ProviderRecord(id="univibe", name="Univibe", models=["openai", "claude", "gemini"], api_url=None)]
        else:
            providers = [ProviderRecord.from_dict(item) for item in providers_data]

        current = dict(data.get("current", {}))

        # Normalize key ids to keep them continuous (1..N). This keeps UX stable
        # even if older configs have gaps or duplicates.
        old_to_new: Dict[str, str] = {}
        for idx, item in enumerate(keys, start=1):
            old_id = str(item.id)
            new_id = str(idx)
            if old_id not in old_to_new:
                old_to_new[old_id] = new_id
            item.id = new_id

        for cli_name, current_id in list(current.items()):
            if not current_id:
                continue
            current[str(cli_name)] = old_to_new.get(str(current_id))

        return cls(
            version=data.get("version", 1),
            current=current,
            keys=keys,
            providers=providers,
        )

    def to_dict(self) -> Dict:
        return {
            "version": self.version,
            "current": self.current,
            "keys": [item.to_dict() for item in self.keys],
            "providers": [item.to_dict() for item in self.providers],
        }


def load_config(path: Optional[Path] = None) -> KeyhubConfig:
    """Load configuration from disk, or return an empty config if missing."""
    target = path or get_config_path()
    if not target.exists():
        return KeyhubConfig.empty()

    import json

    with target.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return KeyhubConfig.from_dict(raw)


def save_config(config: KeyhubConfig, path: Optional[Path] = None) -> None:
    """Persist configuration to disk as pretty-printed JSON."""
    target = path or get_config_path()
    data = config.to_dict()

    import json

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def add_key(
    config: KeyhubConfig,
    *,
    key_id: str,
    name: str,
    provider: str,
    secret: str,
    category: Optional[str] = None,
    note: Optional[str] = None,
    quota_remaining: Optional[str] = None,
    auth_token: Optional[str] = None,
) -> KeyRecord:
    """Add a new key record into the config."""
    record = KeyRecord(
        id=key_id,
        name=name,
        provider=provider,
        cli_targets=[],
        key=secret,
        category=category,
        note=note,
        quota_remaining=quota_remaining,
        auth_token=auth_token,
    )
    config.keys.append(record)
    return record


def get_key(config: KeyhubConfig, key_id: str) -> Optional[KeyRecord]:
    """Return a key record by id."""
    for item in config.keys:
        if item.id == key_id:
            return item
    return None


def update_key(
    config: KeyhubConfig,
    key_id: str,
    *,
    name: Optional[str] = None,
    provider: Optional[str] = None,
    secret: Optional[str] = None,
    category: Optional[str] = None,
    note: Optional[str] = None,
    quota_remaining: Optional[str] = None,
    auth_token: Optional[str] = None,
    status: Optional[str] = None,
) -> bool:
    """Update a key record by id. Return True if updated."""
    record = get_key(config, key_id)
    if not record:
        return False

    if name is not None:
        record.name = name
    if provider is not None:
        record.provider = provider
    if secret is not None:
        record.key = secret
    if category is not None:
        record.category = category
    if note is not None:
        record.note = note
    if quota_remaining is not None:
        record.quota_remaining = quota_remaining
    if auth_token is not None:
        record.auth_token = auth_token
    if status is not None:
        record.status = status

    return True


def delete_key(config: KeyhubConfig, key_id: str) -> bool:
    """Delete a key by id. Return True if removed.

    After deletion, keys are re-numbered to keep ids continuous: 1..N.
    Any current mappings are updated to the new ids.
    """
    before = len(config.keys)
    if before == 0:
        return False

    removed = False
    kept: List[KeyRecord] = []
    for item in config.keys:
        if item.id == key_id:
            removed = True
            continue
        kept.append(item)

    if not removed:
        return False

    id_map: Dict[str, str] = {}
    for idx, item in enumerate(kept, start=1):
        old_id = item.id
        new_id = str(idx)
        item.id = new_id
        id_map[old_id] = new_id

    config.keys = kept

    # Update current mappings.
    for cli_name, current_id in list(config.current.items()):
        if not current_id:
            continue
        config.current[cli_name] = id_map.get(current_id)

    return True


def add_provider(
    config: KeyhubConfig,
    *,
    provider_id: str,
    name: str,
    models: List[str],
    api_url: Optional[str] = None,
    website: Optional[str] = None,
    auth_token: Optional[str] = None,
) -> ProviderRecord:
    """Add or overwrite a provider definition."""
    pid = str(provider_id or "").strip().lower()

    # Remove existing with same id.
    config.providers = [p for p in config.providers if str(p.id).strip().lower() != pid]
    record = ProviderRecord(id=pid, name=name, models=models, api_url=api_url, website=website, auth_token=auth_token)
    config.providers.append(record)
    # Stable sort by id for predictable UI.
    config.providers.sort(key=lambda p: p.id)
    return record


def get_provider(config: KeyhubConfig, provider_id: str) -> Optional[ProviderRecord]:
    pid = str(provider_id or "").strip().lower()
    for item in config.providers:
        if str(item.id).strip().lower() == pid:
            return item
    return None


def update_provider(
    config: KeyhubConfig,
    provider_id: str,
    *,
    name: Optional[str] = None,
    models: Optional[List[str]] = None,
    api_url: Optional[str] = None,
    website: Optional[str] = None,
    auth_token: Optional[str] = None,
) -> bool:
    record = get_provider(config, provider_id)
    if not record:
        return False

    if name is not None:
        record.name = name
    if models is not None:
        record.models = models
    if api_url is not None:
        record.api_url = api_url
    if website is not None:
        record.website = website
    if auth_token is not None:
        record.auth_token = auth_token

    config.providers.sort(key=lambda p: p.id)
    return True


def delete_provider(config: KeyhubConfig, provider_id: str) -> bool:
    before = len(config.providers)
    pid = str(provider_id or "").strip().lower()
    config.providers = [p for p in config.providers if str(p.id).strip().lower() != pid]
    return len(config.providers) < before


def set_current(config: KeyhubConfig, cli_name: str, key_id: Optional[str]) -> None:
    """Set the current key id for a given CLI name."""
    if key_id is not None and not any(item.id == key_id for item in config.keys):
        raise ValueError(f"Key id not found: {key_id}")
    config.current[cli_name] = key_id


def get_current(config: KeyhubConfig, cli_name: str) -> Optional[KeyRecord]:
    """Get the current key record for a given CLI name."""
    key_id = config.current.get(cli_name)
    if not key_id:
        return None
    for item in config.keys:
        if item.id == key_id:
            return item
    return None

