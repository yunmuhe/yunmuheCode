from src.web.admin_views import _display_api_name


def test_display_api_name_maps_baishan_to_chinese_name():
    assert _display_api_name("baishan") == "白山智算"


def test_display_api_name_keeps_unknown_provider_name():
    assert _display_api_name("custom-provider") == "custom-provider"


def test_display_api_name_returns_dash_for_empty_value():
    assert _display_api_name("") == "-"
