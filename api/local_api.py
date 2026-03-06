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
            version="1.0.0",
            message="CodeExplain AI is running.",
        )

    @app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
    def analyze(req: AnalysisRequest) -> AnalysisResponse:
        """Analyze Python source code for complexity, smells, and metrics."""
        from core.parser.ast_parser import ASTParser
        from core.parser.node_mapper import NodeMapper
        from core.analyzer.complexity_analyzer import ComplexityAnalyzer
        from core.analyzer.code_smells import CodeSmellDetector
        from core.analyzer.metrics import MetricsComputer
        from core.scoring.difficulty_score import DifficultyScorer
        from core.scoring.maintainability_score import MaintainabilityScorer

        parser = ASTParser()
        parse_result = parser.parse_source(req.source, filename=req.filename)

        if not parse_result.success:
            raise HTTPException(status_code=400, detail=parse_result.errors[0])

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
        """Generate a human-readable explanation of Python source code."""
        from core.parser.ast_parser import ASTParser
        from core.parser.node_mapper import NodeMapper
        from core.explainer.explanation_engine import ExplanationEngine

        parser = ASTParser()
        parse_result = parser.parse_source(req.source, filename=req.filename)

        if not parse_result.success:
            raise HTTPException(status_code=400, detail=parse_result.errors[0])

        mapper = NodeMapper()
        module = mapper.map(parse_result)

        try:
            engine = ExplanationEngine()
            explanation = engine.explain(module, mode=req.mode)
        except ValueError as e:
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
        from core.parser.ast_parser import ASTParser
        from core.parser.node_mapper import NodeMapper
        from core.analyzer.complexity_analyzer import ComplexityAnalyzer
        from core.analyzer.code_smells import CodeSmellDetector
        from core.analyzer.metrics import MetricsComputer
        from core.explainer.explanation_engine import ExplanationEngine
        from core.scoring.difficulty_score import DifficultyScorer
        from core.scoring.maintainability_score import MaintainabilityScorer
        from utils.formatter import to_html, to_json, to_markdown

        parser = ASTParser()
        parse_result = parser.parse_source(req.source, filename=req.filename)

        if not parse_result.success:
            raise HTTPException(status_code=400, detail=parse_result.errors[0])

        mapper = NodeMapper()
        module = mapper.map(parse_result)

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
            "file": req.filename,
            "metrics": m.summary(),
            "complexity": {
                "overall_label": complexity.overall_label,
                "average_complexity": complexity.average_complexity,
                "max_complexity": complexity.max_complexity,
                "functions": [
                    {"name": f.name, "cyclomatic_complexity": f.cyclomatic_complexity,
                     "nesting_depth": f.nesting_depth, "loop_count": f.loop_count,
                     "has_recursion": f.has_recursion, "complexity_label": f.complexity_label}
                    for f in complexity.functions
                ],
            },
            "smells": [{"kind": s.kind, "severity": s.severity,
                        "message": s.message, "lineno": s.lineno} for s in smells.smells],
            "explanation": explanation,
            "scores": {"difficulty": round(diff.score, 1), "maintainability": maint.rounded},
        }

        fmt = req.format.lower()
        if fmt == "html":
            content = to_html(data)
        elif fmt == "json":
            content = to_json(data)
        elif fmt == "markdown":
            content = to_markdown(data)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown format '{fmt}'")

        return ReportResponse(
            filename=req.filename,
            format=fmt,
            generated_at=datetime.now().isoformat(),
            content=content,
            size_bytes=len(content.encode()),
        )

    return app


# Allow direct running: python api/local_api.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(create_app(), host="127.0.0.1", port=8000, log_level="info")
