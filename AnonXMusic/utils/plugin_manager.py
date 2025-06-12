import time
import importlib
import sys
from pathlib import Path

PLUGIN_DIR = "AnonXMusic/plugins"
loaded_plugins = {}
disabled_plugins = set()


def load_plugin(name):
    try:
        if name in sys.modules:
            importlib.reload(sys.modules[f"AnonXMusic.plugins.{name}"])
        else:
            importlib.import_module(f"AnonXMusic.plugins.{name}")
        loaded_plugins[name] = time.time()
        return True
    except Exception as e:
        return str(e)


def unload_plugin(name):
    module_name = f"AnonXMusic.plugins.{name}"
    if module_name in sys.modules:
        del sys.modules[module_name]
        disabled_plugins.add(name)
        return True
    return False


def list_plugins():
    return sorted([
        f.stem for f in Path(PLUGIN_DIR).glob("*.py")
        if not f.name.startswith("__")
    ])