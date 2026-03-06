"""
Base Plugin — Abstract base class for all CodeExplain AI plugins.

To create a plugin:
1. Create a .py file in the plugins/ directory
2. Subclass BasePlugin
3. Implement the analyze() method
4. Set name, version, description class attributes
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PluginResult:
    """Result returned by a plugin's analyze() method."""
    name: str          # Plugin name
    findings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_findings(self) -> bool:
        return len(self.findings) > 0


class BasePlugin(ABC):
    """
    Abstract base class for CodeExplain AI plugins.

    Example plugin:

        from plugins.base_plugin import BasePlugin, PluginResult

        class SecurityPlugin(BasePlugin):
            name = "security_scanner"
            version = "1.0.0"
            description = "Scans for security issues"

            def analyze(self, module, source):
                findings = []
                if "eval(" in source:
                    findings.append("eval() detected — potential code injection risk")
                if "exec(" in source:
                    findings.append("exec() detected — review carefully")
                return PluginResult(name=self.name, findings=findings)
    """

    # Must be overridden by subclasses
    name: str = "unnamed_plugin"
    version: str = "0.0.0"
    description: str = "No description provided."

    @abstractmethod
    def analyze(self, module, source: str) -> PluginResult:
        """
        Analyze a parsed module and return findings.

        Args:
            module: ModuleNode — the parsed module structure
            source: str — original source code string

        Returns:
            PluginResult with any findings
        """
        ...

    def __repr__(self) -> str:
        return f"<Plugin: {self.name} v{self.version}>"
