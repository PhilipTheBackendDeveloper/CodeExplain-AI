# CodeExplain AI 🧠

> A production-ready static code analysis and explanation engine for Python developers.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What is CodeExplain AI?

**CodeExplain AI** parses Python programs using Abstract Syntax Trees, constructs semantic representations of code structure, performs multi-layer analysis (complexity, dependencies, design quality), and generates human-readable explanations of code logic.

Think: _"Explainable static analysis engine for developers."_

---

## Features

| Feature                   | Description                                              |
| ------------------------- | -------------------------------------------------------- |
| 🔍 **AST Parser**         | Deep code parsing with symbol table                      |
| 📊 **Code Analyzer**      | Complexity, dependencies, code smells, metrics           |
| 🧠 **Explanation Engine** | Beginner, Developer, Fun (pirate/shakespeare/eli5) modes |
| 🌐 **Graph Builder**      | Call graph, control flow, dependency graph               |
| 🎯 **Scoring**            | Difficulty (0–10) and Maintainability (0–100) scores     |
| 🖼️ **Visualization**      | ASCII diagrams, rich tree views, flow charts             |
| 🖥️ **CLI**                | `codeexplain explain/analyze/visualize/report`           |
| 🔌 **Plugin System**      | Extensible architecture for custom analyzers             |
| 🌐 **Local API**          | FastAPI server for programmatic access                   |
| 📄 **Reports**            | HTML, JSON, and Markdown report generation               |

---

## Installation

```bash
git clone https://github.com/yourname/codeexplain-ai
cd codeexplain-ai
pip install -e ".[dev]"
```

---

## Quick Start

```bash
# Explain a Python file
codeexplain explain examples/sample_code_1.py

# Explain in beginner mode
codeexplain explain examples/sample_code_1.py --mode beginner

# Explain in fun pirate mode
codeexplain explain examples/sample_code_1.py --mode fun:pirate

# Full analysis with smells and metrics
codeexplain analyze examples/sample_code_2.py --smells --complexity --metrics

# Visualize call graph
codeexplain visualize examples/sample_code_1.py --call-graph

# Generate HTML report
codeexplain report examples/sample_code_1.py --format html --output report.html

# Start local API server
codeexplain serve
```

---

## CLI Commands

| Command            | Description                                |
| ------------------ | ------------------------------------------ |
| `explain <file>`   | Generate human-readable code explanation   |
| `analyze <file>`   | Analyze complexity, smells, and metrics    |
| `visualize <file>` | Render call/control-flow/dependency graphs |
| `report <file>`    | Generate structured analysis reports       |
| `serve`            | Start the local FastAPI server             |

### Explanation Modes

| Mode              | Description                                    |
| ----------------- | ---------------------------------------------- |
| `developer`       | Technical analysis with complexity notes       |
| `beginner`        | Friendly, jargon-free with analogies           |
| `fun:pirate`      | Arr, matey! Code explained pirate-style        |
| `fun:shakespeare` | Hark! What code through yonder function breaks |
| `fun:eli5`        | Explain like I'm 5                             |

---

## Local API

Start the server:

```bash
codeexplain serve
```

Endpoints:

- `GET  /health` — Health check
- `POST /analyze` — Analyze source code
- `POST /explain` — Explain source code
- `POST /report` — Generate report

---

## Plugin System

Create a custom plugin:

```python
from plugins.base_plugin import BasePlugin, PluginResult

class MySecurityPlugin(BasePlugin):
    name = "security_scanner"
    version = "1.0.0"
    description = "Scans for security issues"

    def analyze(self, code_nodes):
        # your analysis logic here
        return PluginResult(name=self.name, findings=["eval() detected"])
```

Drop it in the `plugins/` directory — it's auto-discovered.

---

## Project Structure

```
codeexplain-ai/
├── core/          # Parser, analyzer, explainer, graph, scoring
├── cli/           # CLI commands (typer + rich)
├── api/           # FastAPI local server
├── visualization/ # ASCII + rich diagrams
├── plugins/       # Plugin system
├── utils/         # File loader, logger, formatter, helpers
├── config/        # YAML configuration
├── tests/         # pytest test suite
├── examples/      # Sample Python files for demo
└── docs/          # Architecture, usage, API reference
```

---

## Running Tests

```bash
pytest tests/ -v --cov=core --cov-report=term-missing
```

---

## License

MIT © CodeExplain AI Team
