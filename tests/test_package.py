"""Test suite for twat_multi."""

def test_version():
    """Verify package exposes version."""
    import twat_multi
    assert twat_multi.__version__

def test_plugin():
    """Verify plugin functionality."""
    import twat_multi
    plugin = twat_multi.Plugin()
    plugin.set("test", "value")
    assert plugin.get("test") == "value"
 