from src.web.dev_server import get_dev_server_options


def test_windows_debug_server_disables_reloader():
    options = get_dev_server_options(debug=True, platform="win32")

    assert options["debug"] is True
    assert options["use_reloader"] is False


def test_main_uses_dev_server_options(monkeypatch):
    import importlib
    import sys
    import types

    calls = {}

    class FakeApp:
        def run(self, **kwargs):
            calls["kwargs"] = kwargs

    fake_name_generator_module = types.ModuleType("src.core.name_generator")
    fake_name_generator_module.name_generator = type(
        "Generator",
        (),
        {"get_available_options": lambda self: {"apis": []}},
    )()
    fake_web_app_module = types.ModuleType("src.web.app")
    fake_web_app_module.app = FakeApp()
    fake_web_app_module.get_config = lambda: {
        "default": type("Cfg", (), {"DEBUG": True})()
    }

    monkeypatch.setitem(sys.modules, "src.core.name_generator", fake_name_generator_module)
    monkeypatch.setitem(sys.modules, "src.web.app", fake_web_app_module)
    monkeypatch.setattr(sys, "platform", "linux")
    sys.modules.pop("main", None)
    main_module = importlib.import_module("main")

    monkeypatch.setattr(main_module.os.path, "exists", lambda path: True)
    monkeypatch.setattr(
        main_module,
        "get_dev_server_options",
        lambda debug, platform=None: {"debug": debug, "use_reloader": False},
        raising=False,
    )
    main_module.main()

    assert calls["kwargs"]["host"] == "0.0.0.0"
    assert calls["kwargs"]["port"] == 5000
    assert calls["kwargs"]["debug"] is True
    assert calls["kwargs"]["use_reloader"] is False
