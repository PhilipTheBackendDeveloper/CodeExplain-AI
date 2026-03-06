"""
Tests for core/explainer/ — All explanation modes
"""

import pytest
from core.parser.ast_parser import ASTParser
from core.parser.node_mapper import NodeMapper
from core.explainer.explanation_engine import ExplanationEngine, VALID_MODES
from core.explainer.beginner_mode import BeginnerExplainer
from core.explainer.developer_mode import DeveloperExplainer
from core.explainer.fun_modes import FunModeExplainer


SAMPLE_CODE = """
\"\"\"A sample module for explanation tests.\"\"\"
import os

class DataProcessor:
    \"\"\"Processes data records.\"\"\"

    def __init__(self, source: str):
        self.source = source

    def process(self, records: list) -> list:
        \"\"\"Process a list of records.\"\"\"
        results = []
        for record in records:
            if record:
                results.append(record.strip())
        return results


def load_data(filepath: str) -> list:
    \"\"\"Load data from a file.\"\"\"
    with open(filepath) as f:
        return f.readlines()


async def fetch_remote(url: str) -> bytes:
    \"\"\"Fetch data from a remote URL.\"\"\"
    pass
"""


@pytest.fixture
def module():
    parser = ASTParser()
    result = parser.parse_source(SAMPLE_CODE)
    mapper = NodeMapper()
    return mapper.map(result)


class TestExplanationEngine:
    def test_developer_mode_returns_string(self, module):
        engine = ExplanationEngine()
        text = engine.explain(module, mode="developer")
        assert isinstance(text, str)
        assert len(text) > 0

    def test_beginner_mode_returns_string(self, module):
        engine = ExplanationEngine()
        text = engine.explain(module, mode="beginner")
        assert isinstance(text, str)
        assert len(text) > 0

    def test_fun_pirate_mode(self, module):
        engine = ExplanationEngine()
        text = engine.explain(module, mode="fun:pirate")
        assert isinstance(text, str)
        assert len(text) > 0
        # Pirate mode should have pirate flavor
        assert any(word in text.lower() for word in ["arr", "pirate", "ahoy", "matey", "captain", "ship"])

    def test_fun_shakespeare_mode(self, module):
        engine = ExplanationEngine()
        text = engine.explain(module, mode="fun:shakespeare")
        assert isinstance(text, str)
        assert len(text) > 0

    def test_fun_eli5_mode(self, module):
        engine = ExplanationEngine()
        text = engine.explain(module, mode="fun:eli5")
        assert isinstance(text, str)
        assert len(text) > 0

    def test_invalid_mode_raises(self, module):
        engine = ExplanationEngine()
        with pytest.raises(ValueError, match="Unknown mode"):
            engine.explain(module, mode="unknown_mode")

    def test_list_modes(self):
        modes = ExplanationEngine.list_modes()
        assert "developer" in modes
        assert "beginner" in modes
        assert "fun:pirate" in modes

    def test_all_valid_modes(self, module):
        engine = ExplanationEngine()
        for mode in VALID_MODES:
            text = engine.explain(module, mode=mode)
            assert len(text) > 10, f"Mode '{mode}' produced empty output"


class TestBeginnerMode:
    def test_produces_non_empty_output(self, module):
        explainer = BeginnerExplainer()
        text = explainer.explain(module)
        assert len(text) > 0

    def test_mentions_function_names(self, module):
        explainer = BeginnerExplainer()
        text = explainer.explain(module)
        assert "load_data" in text or "fetch_remote" in text

    def test_mentions_class_names(self, module):
        explainer = BeginnerExplainer()
        text = explainer.explain(module)
        assert "DataProcessor" in text


class TestDeveloperMode:
    def test_produces_non_empty_output(self, module):
        explainer = DeveloperExplainer()
        text = explainer.explain(module)
        assert len(text) > 0

    def test_includes_type_annotations(self, module):
        explainer = DeveloperExplainer()
        text = explainer.explain(module)
        # Should mention str (from load_data's filepath: str)
        assert "str" in text or "list" in text

    def test_mentions_async(self, module):
        explainer = DeveloperExplainer()
        text = explainer.explain(module)
        assert "async" in text.lower()


class TestFunModes:
    def test_available_modes(self):
        explainer = FunModeExplainer()
        modes = explainer.available_modes()
        assert "pirate" in modes
        assert "shakespeare" in modes
        assert "eli5" in modes

    def test_unknown_fun_mode_raises(self, module):
        explainer = FunModeExplainer()
        with pytest.raises(ValueError):
            explainer.explain(module, mode="robot")
