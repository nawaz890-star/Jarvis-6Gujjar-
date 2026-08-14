from plugins.manager import PluginManager
from tempfile import TemporaryDirectory
from pathlib import Path
import json


def test_sample_plugin_run():
    # Use the sample_echo plugin included in the repository
    pm = PluginManager(plugins_dir=Path('plugins'))
    plugins = pm.list_plugins()
    # Ensure our sample plugin is discovered
    assert any(p['id'] == 'sample.echo' for p in plugins)
    # Run the plugin
    result = pm.run_plugin('sample.echo', {'msg': 'hello'}, timeout=5)
    assert result.get('ok') is True
    assert result.get('echo', {}).get('msg') == 'hello'
