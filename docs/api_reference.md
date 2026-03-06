# API Reference — CodeExplain AI

Base URL: `http://127.0.0.1:8000`

## Endpoints

### `GET /health`

Health check.

**Response:**

```json
{
  "status": "ok",
  "version": "1.0.0",
  "message": "CodeExplain AI is running."
}
```

---

### `POST /analyze`

Analyze Python source code.

**Request Body:**

```json
{
  "source": "def add(a, b):\n    return a + b",
  "filename": "math_utils.py",
  "include_smells": true,
  "include_complexity": true,
  "include_metrics": true,
  "include_scores": true
}
```

**Response:** `AnalysisResponse` with `metrics`, `complexity`, `smells`, `scores`.

---

### `POST /explain`

Explain Python source code in human language.

**Request Body:**

```json
{
  "source": "def greet(name):\n    return f'Hello, {name}!'",
  "filename": "greet.py",
  "mode": "beginner"
}
```

**Modes:** `developer` | `beginner` | `fun:pirate` | `fun:shakespeare` | `fun:eli5`

**Response:**

```json
{
  "filename": "greet.py",
  "mode": "beginner",
  "generated_at": "2026-03-06T12:00:00",
  "explanation": "..."
}
```

---

### `POST /report`

Generate a full analysis report.

**Request Body:**

```json
{
  "source": "...",
  "filename": "my_module.py",
  "format": "html",
  "mode": "developer"
}
```

**Formats:** `html` | `json` | `markdown`

**Response:**

```json
{
  "filename": "my_module.py",
  "format": "html",
  "generated_at": "...",
  "content": "<!DOCTYPE html>...",
  "size_bytes": 12345
}
```

---

## Interactive Docs

Start the server and visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
