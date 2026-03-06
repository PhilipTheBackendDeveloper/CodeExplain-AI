"""
Local API — FastAPI server for CodeExplain AI.

Endpoints:
  GET  /health    — Health check
  POST /analyze   — Analyze source code
  POST /explain   — Explain source code
  POST /report    — Generate report
"""

from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.response_models import (
    AnalysisRequest, AnalysisResponse,
    ExplainRequest, ExplanationResponse,
    ReportRequest, ReportResponse,
    HealthResponse,
    ComplexityModel, FunctionComplexityModel,
    MetricsModel, SmellModel, ScoresModel,
)
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os


def create_app() -> FastAPI:
    """Factory function to create the FastAPI application."""
    app = FastAPI(
        title="CodeExplain AI",
        description="Professional static code analysis and explanation engine.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse, tags=["System"])
    def health() -> HealthResponse:
        """Health check endpoint."""
        return HealthResponse(
            status="ok",
            version="1.1.0",
            message="CodeExplain AI (Multi-Lang) is running.",
        )

    @app.get("/api/files", tags=["Explorer"])
    def list_files(path: str = "."):
        """List files in the project for the dashboard explorer."""
        base_path = Path(path).resolve()
        exclude = {".git", "__pycache__", "node_modules", ".venv", ".pytest_cache", "ui"}
        
        files = []
        for root, dirs, filenames in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in exclude]
            for f in filenames:
                if f.endswith((".py", ".ts", ".tsx", ".js", ".jsx")):
                    rel = os.path.relpath(os.path.join(root, f), base_path)
                    files.append({"name": f, "path": rel.replace("\\", "/")})
        return sorted(files, key=lambda x: x['path'])

    @app.get("/api/file-content", tags=["Explorer"])
    def get_file_content(path: str):
        """Fetch content of a specific file."""
        p = Path(path)
        if not p.exists():
            raise HTTPException(status_code=404, detail="File not found")
        return {"content": p.read_text(encoding="utf-8")}

    @app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
    def analyze(req: AnalysisRequest) -> AnalysisResponse:
        """Analyze source code for complexity, smells, and metrics."""
        from core.parser.factory import UniversalParser
        from core.analyzer.complexity_analyzer import ComplexityAnalyzer
        from core.analyzer.code_smells import CodeSmellDetector
        from core.analyzer.metrics import MetricsComputer
        from core.scoring.difficulty_score import DifficultyScorer
        from core.scoring.maintainability_score import MaintainabilityScorer

        u_parser = UniversalParser()
        try:
            module = u_parser.parse_and_map(Path(req.source_path)) if getattr(req, 'source_path', None) else None
            # Fallback for direct source if path not provided
            if not module:
                from core.parser.ast_parser import ASTParser
                from core.parser.node_mapper import NodeMapper
                p = ASTParser()
                pr = p.parse_source(req.source, filename=req.filename)
                if not pr.success:
                    raise HTTPException(status_code=400, detail=pr.errors[0])
                module = NodeMapper().map(pr)
                parse_result = pr
            else:
                # If we have a path, we might want to re-parse as AST for python-only features
                from core.parser.ast_parser import ASTParser
                p = ASTParser()
                parse_result = p.parse_source(req.source, filename=req.filename)
        except Exception as e:
             raise HTTPException(status_code=400, detail=str(e))

        now = datetime.now().isoformat()
        response = AnalysisResponse(filename=req.filename, generated_at=now)

        if req.include_metrics:
            mc = MetricsComputer()
            m = mc.compute(parse_result)
            summary = m.summary()
            response.metrics = MetricsModel(
                total_lines=m.total_lines,
                source_lines=m.source_lines,
                blank_lines=m.blank_lines,
                comment_lines=m.comment_lines,
                comment_ratio=round(m.comment_ratio, 4),
                function_count=m.function_count,
                class_count=m.class_count,
                import_count=m.import_count,
                halstead_volume=round(m.halstead_volume, 2),
                halstead_difficulty=round(m.halstead_difficulty, 2),
            )

        if req.include_complexity:
            ca = ComplexityAnalyzer()
            complexity = ca.analyze(parse_result)
            response.complexity = ComplexityModel(
                overall_label=complexity.overall_label,
                average_complexity=round(complexity.average_complexity, 2),
                max_complexity=complexity.max_complexity,
                functions=[
                    FunctionComplexityModel(
                        name=f.name,
                        cyclomatic_complexity=f.cyclomatic_complexity,
                        nesting_depth=f.nesting_depth,
                        loop_count=f.loop_count,
                        has_recursion=f.has_recursion,
                        complexity_label=f.complexity_label,
                    )
                    for f in complexity.functions
                ],
            )

        if req.include_smells:
            detector = CodeSmellDetector()
            smells = detector.detect(parse_result)
            response.smells = [
                SmellModel(kind=s.kind, severity=s.severity, message=s.message, lineno=s.lineno)
                for s in smells.smells
            ]

        if req.include_scores and response.complexity and response.metrics:
            ca2 = ComplexityAnalyzer()
            mx2 = MetricsComputer()
            comp = ca2.analyze(parse_result)
            met = mx2.compute(parse_result)
            smells_cnt = len(response.smells) if response.smells else 0

            diff_scorer = DifficultyScorer()
            diff = diff_scorer.score(comp, smells_count=smells_cnt)

            maint_scorer = MaintainabilityScorer()
            maint = maint_scorer.score(met, comp)

            response.scores = ScoresModel(
                difficulty=round(diff.score, 1),
                difficulty_label=diff.label,
                maintainability=maint.rounded,
                maintainability_label=maint.label,
            )

        return response

    @app.post("/explain", response_model=ExplanationResponse, tags=["Explanation"])
    def explain(req: ExplainRequest) -> ExplanationResponse:
        """Generate a human-readable explanation of source code."""
        from core.parser.factory import UniversalParser
        from core.explainer.explanation_engine import ExplanationEngine

        u_parser = UniversalParser()
        try:
            if req.source_path and Path(req.source_path).exists():
                module = u_parser.parse_and_map(Path(req.source_path))
            else:
                from core.parser.ast_parser import ASTParser
                from core.parser.node_mapper import NodeMapper
                p = ASTParser()
                pr = p.parse_source(req.source, filename=req.filename)
                if not pr.success:
                    raise HTTPException(status_code=400, detail=pr.errors[0])
                module = NodeMapper().map(pr)
            
            engine = ExplanationEngine()
            explanation = engine.explain(module, mode=req.mode)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        return ExplanationResponse(
            filename=req.filename,
            mode=req.mode,
            generated_at=datetime.now().isoformat(),
            explanation=explanation,
        )

    @app.post("/report", response_model=ReportResponse, tags=["Reports"])
    def generate_report(req: ReportRequest) -> ReportResponse:
        """Generate a full analysis report in JSON, HTML, or Markdown."""
        from core.parser.factory import UniversalParser
        from core.explainer.explanation_engine import ExplanationEngine
        from utils.formatter import to_html, to_json, to_markdown

        u_parser = UniversalParser()
        try:
            p = Path(req.source_path) if req.source_path else None
            is_python = (p.suffix.lower() == ".py") if (p and p.suffix) else True
            
            module = u_parser.parse_and_map(p) if p else None
            if not module:
                from core.parser.ast_parser import ASTParser
                from core.parser.node_mapper import NodeMapper
                parser = ASTParser()
                parse_result = parser.parse_source(req.source, filename=req.filename)
                if not parse_result.success:
                    raise HTTPException(status_code=400, detail=parse_result.errors[0])
                module = NodeMapper().map(parse_result)
            elif is_python:
                from core.parser.ast_parser import ASTParser
                parser = ASTParser()
                parse_result = parser.parse_source(req.source, filename=req.filename)
            else:
                parse_result = None

            if is_python and parse_result:
                from core.analyzer.complexity_analyzer import ComplexityAnalyzer
                from core.analyzer.code_smells import CodeSmellDetector
                from core.analyzer.metrics import MetricsComputer
                from core.scoring.difficulty_score import DifficultyScorer
                from core.scoring.maintainability_score import MaintainabilityScorer

                mc = MetricsComputer()
                m = mc.compute(parse_result)
                ca = ComplexityAnalyzer()
                complexity = ca.analyze(parse_result)
                detector = CodeSmellDetector()
                smells = detector.detect(parse_result)
                engine = ExplanationEngine()
                explanation = engine.explain(module, mode=req.mode)
                diff = DifficultyScorer().score(complexity, smells_count=smells.total_count)
                maint = MaintainabilityScorer().score(m, complexity)

                data = {
                    "file": req.filename, "metrics": m.summary(),
                    "complexity": {
                        "overall_label": complexity.overall_label,
                        "average_complexity": complexity.average_complexity,
                        "max_complexity": complexity.max_complexity,
                        "functions": [{"name": f.name, "cyclomatic_complexity": f.cyclomatic_complexity, "has_recursion": f.has_recursion} for f in complexity.functions],
                    },
                    "smells": [{"kind": s.kind, "message": s.message} for s in smells.smells],
                    "explanation": explanation,
                    "scores": {"difficulty": round(diff.score, 1), "maintainability": maint.rounded},
                }
            else:
                engine = ExplanationEngine()
                explanation = engine.explain(module, mode=req.mode)
                data = {
                    "file": req.filename, "metrics": {"total_lines": module.line_count},
                    "complexity": {"overall_label": "Unknown", "functions": []},
                    "smells": [], "explanation": explanation, "scores": {"difficulty": 0, "maintainability": 0},
                }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        fmt = req.format.lower()
        content = to_html(data) if fmt == "html" else to_json(data) if fmt == "json" else to_markdown(data)

        return ReportResponse(
            filename=req.filename,
            format=fmt,
            generated_at=datetime.now().isoformat(),
            content=content,
            size_bytes=len(content.encode()),
        )

    # Serve Dashboard UI
    ui_dist = Path("ui/dist")
    if ui_dist.exists():
        app.mount("/", StaticFiles(directory=ui_dist, html=True), name="ui")
    
    return app


# Allow direct running: python api/local_api.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(create_app(), host="127.0.0.1", port=8000, log_level="info")
