"""
Formatter — Converts analysis results to JSON, HTML, and Markdown outputs.

Uses Jinja2 templates for HTML rendering.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, BaseLoader


# ── Markdown Formatter ──────────────────────────────────────────────────────

def to_markdown(data: dict[str, Any], title: str = "CodeExplain AI Report") -> str:
    """Convert analysis data dict to a Markdown report string."""
    lines = [f"# {title}", f"", f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]

    if "file" in data:
        lines += [f"**File:** `{data['file']}`", ""]

    if "metrics" in data:
        m = data["metrics"]
        lines += [
            "## 📊 Code Metrics",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Lines | {m.get('total_lines', 0)} |",
            f"| Source Lines (SLOC) | {m.get('source_lines', 0)} |",
            f"| Comment Lines | {m.get('comment_lines', 0)} |",
            f"| Blank Lines | {m.get('blank_lines', 0)} |",
            f"| Functions | {m.get('function_count', 0)} |",
            f"| Classes | {m.get('class_count', 0)} |",
            f"| Imports | {m.get('import_count', 0)} |",
            "",
        ]

    if "complexity" in data:
        c = data["complexity"]
        lines += [
            "## 🔄 Complexity",
            "",
            f"**Overall:** {c.get('overall_label', 'N/A')} | "
            f"**Average CC:** {c.get('average_complexity', 0):.1f} | "
            f"**Max CC:** {c.get('max_complexity', 0)}",
            "",
        ]
        if "functions" in c:
            lines += ["| Function | Cyclomatic | Nesting | Loops | Recursive |", "|---|---|---|---|---|"]
            for f in c["functions"]:
                lines.append(
                    f"| `{f['name']}` | {f['cyclomatic_complexity']} | "
                    f"{f['nesting_depth']} | {f['loop_count']} | {'✓' if f['has_recursion'] else '✗'} |"
                )
            lines.append("")

    if "smells" in data:
        smells = data["smells"]
        lines += [f"## 🔍 Code Smells ({len(smells)} found)", ""]
        for s in smells:
            emoji = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(s["severity"], "•")
            lines.append(f"- {emoji} **L{s['lineno']}** `{s['kind']}`: {s['message']}")
        lines.append("")

    if "explanation" in data:
        lines += ["## 🧠 Explanation", "", data["explanation"], ""]

    if "scores" in data:
        s = data["scores"]
        lines += [
            "## 🎯 Scores",
            "",
            f"| Score | Value |",
            f"|-------|-------|",
            f"| Difficulty | {s.get('difficulty', 0)}/10 |",
            f"| Maintainability | {s.get('maintainability', 0)}/100 |",
            "",
        ]

    return "\n".join(lines)


# ── JSON Formatter ──────────────────────────────────────────────────────────

def to_json(data: dict[str, Any], indent: int = 2) -> str:
    """Serialize analysis data to a pretty-printed JSON string."""
    payload = {"generated_at": datetime.now().isoformat(), **data}
    return json.dumps(payload, indent=indent, default=str)


# ── HTML Template ───────────────────────────────────────────────────────────

_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CodeExplain AI — {{ title }}</title>
<style>
  :root {
    --bg: #0d1117; --surface: #161b22; --border: #30363d;
    --text: #c9d1d9; --muted: #8b949e; --accent: #58a6ff;
    --green: #3fb950; --yellow: #d29922; --red: #f85149;
    --purple: #bc8cff;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif;
         font-size: 14px; line-height: 1.6; padding: 24px; }
  h1 { font-size: 2rem; background: linear-gradient(135deg, #58a6ff, #bc8cff);
       -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 4px; }
  h2 { font-size: 1.1rem; color: var(--accent); margin: 24px 0 12px;
       border-bottom: 1px solid var(--border); padding-bottom: 6px; }
  .subtitle { color: var(--muted); margin-bottom: 24px; font-size: 0.85rem; }
  .card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
          padding: 16px; margin-bottom: 16px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }
  .metric { background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
            padding: 12px; text-align: center; }
  .metric .value { font-size: 1.8rem; font-weight: 700; color: var(--accent); }
  .metric .label { font-size: 0.75rem; color: var(--muted); margin-top: 2px; }
  table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
  th { background: var(--bg); color: var(--muted); padding: 8px 12px; text-align: left;
       border-bottom: 2px solid var(--border); font-weight: 600; }
  td { padding: 7px 12px; border-bottom: 1px solid var(--border); }
  tr:hover td { background: rgba(88,166,255,0.05); }
  code { background: var(--bg); padding: 1px 6px; border-radius: 4px;
         font-family: 'Cascadia Code', 'Fira Code', monospace; color: var(--purple); }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.72rem;
           font-weight: 600; }
  .badge-green { background: rgba(63,185,80,0.15); color: var(--green); }
  .badge-yellow { background: rgba(210,153,34,0.15); color: var(--yellow); }
  .badge-red { background: rgba(248,81,73,0.15); color: var(--red); }
  .smell-error { border-left: 3px solid var(--red); }
  .smell-warning { border-left: 3px solid var(--yellow); }
  .smell-info { border-left: 3px solid var(--accent); }
  .smell-item { padding: 8px 12px; margin-bottom: 6px; border-radius: 0 6px 6px 0;
                background: var(--bg); }
  .explanation-text { white-space: pre-wrap; font-size: 0.9rem; line-height: 1.8;
                       color: var(--text); }
  .score-bar { height: 8px; border-radius: 4px; background: var(--border); margin-top: 6px; }
  .score-fill { height: 100%; border-radius: 4px; }
  footer { margin-top: 32px; padding-top: 16px; border-top: 1px solid var(--border);
           color: var(--muted); font-size: 0.8rem; text-align: center; }
</style>
</head>
<body>
<h1>🧠 CodeExplain AI</h1>
<div class="subtitle">Generated: {{ generated_at }} | File: <code>{{ file }}</code></div>

{% if metrics %}
<h2>📊 Code Metrics</h2>
<div class="card">
  <div class="grid">
    <div class="metric"><div class="value">{{ metrics.total_lines }}</div><div class="label">Total Lines</div></div>
    <div class="metric"><div class="value">{{ metrics.source_lines }}</div><div class="label">Source Lines</div></div>
    <div class="metric"><div class="value">{{ metrics.function_count }}</div><div class="label">Functions</div></div>
    <div class="metric"><div class="value">{{ metrics.class_count }}</div><div class="label">Classes</div></div>
    <div class="metric"><div class="value">{{ metrics.import_count }}</div><div class="label">Imports</div></div>
    <div class="metric"><div class="value">{{ "%.0f"|format(metrics.comment_ratio * 100) }}%</div><div class="label">Comment Ratio</div></div>
  </div>
</div>
{% endif %}

{% if complexity %}
<h2>🔄 Complexity Analysis</h2>
<div class="card">
  <p style="margin-bottom:12px">
    Overall: <strong>{{ complexity.overall_label }}</strong> &nbsp;|&nbsp;
    Average CC: <strong>{{ "%.1f"|format(complexity.average_complexity) }}</strong> &nbsp;|&nbsp;
    Max CC: <strong>{{ complexity.max_complexity }}</strong>
  </p>
  {% if complexity.functions %}
  <table>
    <thead><tr><th>Function</th><th>CC</th><th>Nesting</th><th>Loops</th><th>Recursive</th></tr></thead>
    <tbody>
    {% for f in complexity.functions %}
    <tr>
      <td><code>{{ f.name }}</code></td>
      <td>
        {% if f.cyclomatic_complexity <= 5 %}<span class="badge badge-green">{{ f.cyclomatic_complexity }}</span>
        {% elif f.cyclomatic_complexity <= 10 %}<span class="badge badge-yellow">{{ f.cyclomatic_complexity }}</span>
        {% else %}<span class="badge badge-red">{{ f.cyclomatic_complexity }}</span>{% endif %}
      </td>
      <td>{{ f.nesting_depth }}</td>
      <td>{{ f.loop_count }}</td>
      <td>{% if f.has_recursion %}🔁 Yes{% else %}—{% endif %}</td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
  {% endif %}
</div>
{% endif %}

{% if smells %}
<h2>🔍 Code Smells ({{ smells|length }} found)</h2>
<div class="card">
  {% for s in smells %}
  <div class="smell-item smell-{{ s.severity }}">
    {% if s.severity == "error" %}❌{% elif s.severity == "warning" %}⚠️{% else %}ℹ️{% endif %}
    <strong>L{{ s.lineno }}</strong> <code>{{ s.kind }}</code> — {{ s.message }}
  </div>
  {% endfor %}
</div>
{% endif %}

{% if explanation %}
<h2>🧠 Explanation</h2>
<div class="card"><div class="explanation-text">{{ explanation }}</div></div>
{% endif %}

{% if scores %}
<h2>🎯 Scores</h2>
<div class="card grid">
  <div class="metric">
    <div class="value" style="color:#f85149">{{ scores.difficulty }}<span style="font-size:1rem">/10</span></div>
    <div class="label">Difficulty</div>
    <div class="score-bar"><div class="score-fill" style="width:{{ scores.difficulty * 10 }}%;background:#f85149"></div></div>
  </div>
  <div class="metric">
    <div class="value" style="color:#3fb950">{{ scores.maintainability }}<span style="font-size:1rem">/100</span></div>
    <div class="label">Maintainability</div>
    <div class="score-bar"><div class="score-fill" style="width:{{ scores.maintainability }}%;background:#3fb950"></div></div>
  </div>
</div>
{% endif %}

<footer>CodeExplain AI v1.0.0 — Professional Static Analysis Engine</footer>
</body>
</html>
"""


def to_html(data: dict[str, Any], title: str = "Analysis Report") -> str:
    """Render analysis data to an HTML report string using Jinja2."""
    env = Environment(loader=BaseLoader())
    template = env.from_string(_HTML_TEMPLATE)
    return template.render(
        title=title,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        file=data.get("file", "<unknown>"),
        metrics=data.get("metrics"),
        complexity=data.get("complexity"),
        smells=data.get("smells", []),
        explanation=data.get("explanation"),
        scores=data.get("scores"),
    )
