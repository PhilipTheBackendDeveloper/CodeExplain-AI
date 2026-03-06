"""
Response Models — Pydantic models for the CodeExplain AI API.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class AnalysisRequest(BaseModel):
    source: str = Field(..., description="Python source code to analyze")
    filename: str = Field(default="<string>", description="Optional filename for context")
    include_smells: bool = Field(default=True)
    include_complexity: bool = Field(default=True)
    include_metrics: bool = Field(default=True)
    include_scores: bool = Field(default=True)
    source_path: Optional[str] = Field(default=None, description="Path to local file")


class ExplainRequest(BaseModel):
    source: str = Field(..., description="Python source code to explain")
    filename: str = Field(default="<string>")
    mode: str = Field(default="developer", description="developer | beginner | fun:pirate | fun:shakespeare | fun:eli5")
    source_path: Optional[str] = Field(default=None)


class ReportRequest(BaseModel):
    source: str = Field(..., description="Python source code")
    filename: str = Field(default="<string>")
    format: str = Field(default="json", description="json | html | markdown")
    mode: str = Field(default="developer")
    source_path: Optional[str] = Field(default=None)


class FunctionComplexityModel(BaseModel):
    name: str
    cyclomatic_complexity: int
    nesting_depth: int
    loop_count: int
    has_recursion: bool
    complexity_label: str


class ComplexityModel(BaseModel):
    overall_label: str
    average_complexity: float
    max_complexity: int
    functions: list[FunctionComplexityModel]


class SmellModel(BaseModel):
    kind: str
    severity: str
    message: str
    lineno: int


class MetricsModel(BaseModel):
    total_lines: int
    source_lines: int
    blank_lines: int
    comment_lines: int
    comment_ratio: float
    function_count: int
    class_count: int
    import_count: int
    halstead_volume: float
    halstead_difficulty: float


class ScoresModel(BaseModel):
    difficulty: float
    difficulty_label: str
    maintainability: int
    maintainability_label: str


class AnalysisResponse(BaseModel):
    filename: str
    generated_at: str
    metrics: Optional[MetricsModel] = None
    complexity: Optional[ComplexityModel] = None
    smells: Optional[list[SmellModel]] = None
    scores: Optional[ScoresModel] = None


class ExplanationResponse(BaseModel):
    filename: str
    mode: str
    generated_at: str
    explanation: str


class ReportResponse(BaseModel):
    filename: str
    format: str
    generated_at: str
    content: str
    size_bytes: int


class HealthResponse(BaseModel):
    status: str
    version: str
    message: str
