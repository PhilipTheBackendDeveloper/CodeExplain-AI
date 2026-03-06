"""
Plugin Loader — Discovers and loads plugins from the plugins/ directory.

Auto-discovers all BasePlugin subclasses in Python files within the plugins folder.
"""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Type

from plugins.base_plugin import BasePlugin, PluginResult
from utils.logger import get_logger

logger = get_logger(__name__)


class PluginLoader:
    """
    Discovers and loads plugins from a directory.

    Usage:
        loader = PluginLoader()
        plugins = loader.load_all()
        results = loader.run_all(module_node, source_code)
    """

    def __init__(self, plugin_dir: str | Path | None = None):
        if plugin_dir is None:
            plugin_dir = Path(__file__).parent
        self._plugin_dir = Path(plugin_dir)
        self._loaded: list[BasePlugin] = []

    def load_all(self) -> list[BasePlugin]:
        """Discover and instantiate all BasePlugin subclasses in the plugin directory."""
        plugins: list[BasePlugin] = []

        for py_file in self._plugin_dir.glob("*.py"):
            if py_file.stem.startswith("_") or py_file.stem in ("base_plugin", "plugin_loader"):
                continue

            module_name = f"_plugin_{py_file.stem}"
            try:
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec is None or spec.loader is None:
                    continue
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BasePlugin)
                        and attr is not BasePlugin
                    ):
                        try:
                            instance = attr()
                            plugins.append(instance)
                            logger.info(f"Loaded plugin: {instance.name} v{instance.version}")
                        except Exception as e:
                            logger.warning(f"Could not instantiate plugin '{attr_name}': {e}")

            except Exception as e:
                logger.warning(f"Could not load plugin file '{py_file.name}': {e}")

        self._loaded = plugins
        return plugins

    def run_all(self, module, source: str) -> list[PluginResult]:
        """Run all loaded plugins on the given module."""
        if not self._loaded:
            self.load_all()

        results = []
        for plugin in self._loaded:
            try:
                result = plugin.analyze(module, source)
                results.append(result)
                logger.debug(f"Plugin '{plugin.name}' returned {len(result.findings)} findings")
            except Exception as e:
                logger.warning(f"Plugin '{plugin.name}' failed: {e}")
                results.append(PluginResult(name=plugin.name, findings=[f"Plugin error: {e}"]))
        return results

    @property
    def loaded_plugins(self) -> list[BasePlugin]:
        return list(self._loaded)
