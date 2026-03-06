# Roadmap — CodeExplain AI

## v1.0.0 — Current Release ✅

- [x] Python AST parser with full semantic node mapping
- [x] Symbol table with scope-aware resolution
- [x] Cyclomatic complexity analysis
- [x] Code smell detection (8 smell types)
- [x] Halstead metrics computation
- [x] Dependency analysis with categorization
- [x] 5 explanation modes (developer, beginner, pirate, shakespeare, eli5)
- [x] Call graph, control flow graph, dependency graph builders
- [x] Difficulty score (0–10) and Maintainability Index (0–100)
- [x] ASCII diagrams and Rich-based visualization
- [x] CLI with explain/analyze/visualize/report/serve commands
- [x] FastAPI local server with /analyze, /explain, /report endpoints
- [x] Plugin system with auto-discovery
- [x] HTML/JSON/Markdown report generation
- [x] Comprehensive pytest test suite

## v1.1.0 — Near Future

- [ ] **Type inference** — Infer types from usage patterns
- [ ] **Dead code detection** — Functions/classes never called
- [ ] **Circular import detection** — Graph-based cycle detection
- [ ] **Git integration** — `blame`-based author annotations
- [ ] **Diff mode** — Explain changes between two versions of a file
- [ ] **Watch mode** — `codeexplain watch myfile.py` for live analysis

## v1.2.0 — Medium Term

- [ ] **JavaScript support** — Basic JS/TS AST parsing (via tree-sitter)
- [ ] **Security scanner plugin** — Detect `eval`, `exec`, SQL injection risks
- [ ] **Test coverage integration** — Highlight uncovered paths
- [ ] **VSCode Extension** — Right-click → Explain This Function
- [ ] **Web UI** — Simple browser dashboard for browsing analysis results

## v2.0.0 — Future Vision

- [ ] **Multi-file project analysis** — Cross-file call graphs
- [ ] **LLM hybrid mode** — Optional GPT/Gemini integration for better NLG
- [ ] **Team dashboards** — Track code quality trends over time
- [ ] **CI/CD integration** — GitHub Actions workflow for PR analysis
- [ ] **Java/Go/Rust support** — Tree-sitter based multi-language parsing
