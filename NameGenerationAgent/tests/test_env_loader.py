import os
from pathlib import Path
from uuid import uuid4


def test_load_env_file_preserves_existing_environment_variables(monkeypatch):
    env_file = Path(__file__).resolve().parent / f".env.test-{uuid4().hex}"
    try:
        env_file.write_text(
            "SILICONFLOW_API_KEY=file-value\nPAIOU_API_KEY=file-only\n",
            encoding="utf-8",
        )

        monkeypatch.setenv("SILICONFLOW_API_KEY", "runtime-value")
        monkeypatch.delenv("PAIOU_API_KEY", raising=False)

        from src.utils.env_loader import load_env_file

        load_env_file(str(env_file))

        assert os.environ["SILICONFLOW_API_KEY"] == "runtime-value"
        assert os.environ["PAIOU_API_KEY"] == "file-only"
    finally:
        env_file.unlink(missing_ok=True)


def test_load_env_file_tracks_value_source(monkeypatch):
    env_file = Path(__file__).resolve().parent / f".env.test-{uuid4().hex}"
    try:
        env_file.write_text(
            "SILICONFLOW_API_KEY=file-value\nPAIOU_API_KEY=file-only\n",
            encoding="utf-8",
        )

        monkeypatch.setenv("SILICONFLOW_API_KEY", "runtime-value")
        monkeypatch.delenv("PAIOU_API_KEY", raising=False)

        from src.utils import env_loader

        env_loader._ENV_SOURCES.pop("SILICONFLOW_API_KEY", None)
        env_loader._ENV_SOURCES.pop("PAIOU_API_KEY", None)

        env_loader.load_env_file(str(env_file))

        assert env_loader.get_env_source("SILICONFLOW_API_KEY") == "process_env"
        assert env_loader.get_env_source("PAIOU_API_KEY") == ".env"
    finally:
        env_file.unlink(missing_ok=True)
