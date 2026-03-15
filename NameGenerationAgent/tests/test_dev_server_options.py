from src.web.dev_server import get_dev_server_options


def test_windows_debug_server_disables_reloader():
    options = get_dev_server_options(debug=True, platform="win32")

    assert options["debug"] is True
    assert options["use_reloader"] is False
