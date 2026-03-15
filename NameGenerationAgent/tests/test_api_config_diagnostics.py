import types


def test_summarize_api_configurations_masks_secret_and_reports_source(monkeypatch):
    monkeypatch.setenv("ALIYUN_API_KEY", "runtime-secret-value")

    from src.utils import env_loader
    from config import api_config as api_config_module

    env_loader._ENV_SOURCES["ALIYUN_API_KEY"] = "process_env"

    configs = {
        "aliyun": types.SimpleNamespace(
            api_key="runtime-secret-value",
            model="qwen-turbo",
            base_url="https://example.com",
            enabled=True,
        )
    }

    summary = api_config_module.summarize_api_configurations(configs)

    assert summary["aliyun"]["api_key_source"] == "process_env"
    assert summary["aliyun"]["api_key_masked"].startswith("run***")
    assert summary["aliyun"]["api_key_masked"].endswith("lue")
    assert summary["aliyun"]["model"] == "qwen-turbo"
