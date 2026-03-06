# Architecture Overview — CodeExplain AI

## System Architecture

```
Input File
    │
    ▼
┌─────────────────┐
│   ASTParser     │  → ParseResult (ast.Module + metadata)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   NodeMapper    │  → ModuleNode (functions, classes, imports)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌──────────────┐
│Analyzer│  │ SymbolTable  │
│        │  │              │
│Complexity│  Dependency  │
│Smells  │  Graph        │
│Metrics │  │              │
└────┬───┘  └──────────────┘
     │
     ▼
┌─────────────────┐
│    Scorers      │  → DifficultyScore, MaintainabilityScore
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ExplanationEngine│  → Text output (developer/beginner/fun)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│  CLI   │ │   API    │
│ typer  │ │ FastAPI  │
└────────┘ └──────────┘
```

## Layers

| Layer             | Modules                                                                | Responsibility            |
| ----------------- | ---------------------------------------------------------------------- | ------------------------- |
| **Parser**        | `ast_parser`, `node_mapper`, `symbol_table`                            | Code ingestion            |
| **Analyzer**      | `complexity_analyzer`, `dependency_analyzer`, `code_smells`, `metrics` | Code quality analysis     |
| **Explainer**     | `explanation_engine`, `*_mode`                                         | Human language generation |
| **Graph**         | `call_graph`, `control_flow`, `dependency_graph`                       | Structure visualization   |
| **Scoring**       | `difficulty_score`, `maintainability_score`                            | Quality metrics           |
| **Visualization** | `ascii_diagrams`, `graph_renderer`, `flow_visualizer`                  | Output rendering          |
| **CLI**           | `main_cli`, `commands/*`                                               | User interface            |
| **API**           | `local_api`, `response_models`                                         | REST interface            |
| **Plugins**       | `base_plugin`, `plugin_loader`                                         | Extensibility             |

## Data Flow

1. **Source Code** → `ASTParser.parse_source()` → `ParseResult`
2. `ParseResult` → `NodeMapper.map()` → `ModuleNode`
3. `ParseResult` → `ComplexityAnalyzer.analyze()` → `ModuleComplexity`
4. `ParseResult` → `CodeSmellDetector.detect()` → `SmellReport`
5. `ParseResult` → `MetricsComputer.compute()` → `CodeMetrics`
6. `ModuleNode` → `ExplanationEngine.explain()` → `str`
7. `ModuleComplexity` → `DifficultyScorer.score()` → `DifficultyScore`
8. `CodeMetrics + ModuleComplexity` → `MaintainabilityScorer.score()` → `MaintainabilityScore`
9. All results → `Formatter.to_html/json/markdown()` → Report file

## Key Design Decisions

- **No external AI required** — fully offline, deterministic output
- **Template-based NLG** — explanations from metadata, not ML
- **Configuration-driven rules** — all thresholds in `config/rules.yaml`
- **Plugin isolation** — plugins cannot break core analysis
- **Factory pattern** — `create_app()` for testable FastAPI instance
