# Usage Guide — CodeExplain AI

## Installation

```bash
git clone https://github.com/yourname/codeexplain-ai
cd codeexplain-ai
pip install -e ".[dev]"
```

## CLI Usage

### Explain a File

```bash
# Developer mode (default)
codeexplain explain myfile.py

# Beginner-friendly mode
codeexplain explain myfile.py --mode beginner

# Fun modes
codeexplain explain myfile.py --mode fun:pirate
codeexplain explain myfile.py --mode fun:shakespeare
codeexplain explain myfile.py --mode fun:eli5

# Save output to Markdown
codeexplain explain myfile.py --output markdown --save explanation.md

# JSON output
codeexplain explain myfile.py --output json
```

### Analyze a File

```bash
# Full analysis (complexity + smells + metrics + scores)
codeexplain analyze myfile.py

# Only complexity
codeexplain analyze myfile.py --no-smells --no-metrics

# Only metrics
codeexplain analyze myfile.py --no-complexity --no-smells
```

### Visualize Code Structure

```bash
# Module tree (default)
codeexplain visualize myfile.py

# Call graph
codeexplain visualize myfile.py --call-graph

# Control flow graphs
codeexplain visualize myfile.py --control-flow

# Dependency graph
codeexplain visualize myfile.py --dependency-graph

# All visualizations
codeexplain visualize myfile.py --call-graph --control-flow --dependency-graph
```

### Generate Reports

```bash
# HTML report (opens in browser with --open)
codeexplain report myfile.py --format html --output report.html --open

# JSON report
codeexplain report myfile.py --format json --output analysis.json

# Markdown report
codeexplain report myfile.py --format markdown --output report.md
```

### Start the Local API

```bash
codeexplain serve                          # Default: localhost:8000
codeexplain serve --host 0.0.0.0 --port 9000
```

## Python API Usage

```python
from core.parser.ast_parser import ASTParser
from core.parser.node_mapper import NodeMapper
from core.analyzer.complexity_analyzer import ComplexityAnalyzer
from core.explainer.explanation_engine import ExplanationEngine

# Parse
parser = ASTParser()
result = parser.parse_file("myfile.py")

# Map to semantic nodes
module = NodeMapper().map(result)

# Analyze complexity
complexity = ComplexityAnalyzer().analyze(result)
print(f"Average CC: {complexity.average_complexity}")

# Explain
engine = ExplanationEngine()
explanation = engine.explain(module, mode="developer")
print(explanation)
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=core --cov-report=term-missing

# Single module
pytest tests/test_parser.py -v
```
