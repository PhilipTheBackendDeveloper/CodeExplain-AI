# CodeExplain AI 🧠✨

> Understand everything. From abstract code to human stories.

**CodeExplain AI** is a premium static code analysis and narrative explanation engine. It doesn't just parse your code—it tells its story. Designed for absolute beginners and seasoned engineers alike, it transforms complex source code into friendly, jargon-free narratives.

![CodeExplain Dashboard](/ui/public/illustration.png)

---

## 🌟 Key Features

| Feature                  | Description                                                                                   |
| :----------------------- | :-------------------------------------------------------------------------------------------- |
| � **Story Mode AI**      | Overhauled beginner mode that uses metaphors (helpers, blueprints, recipes) to explain logic. |
| 🖥️ **Premium Dashboard** | Clean, Peter Takra-inspired React UI with a minimal white aesthetic and 3D icons.             |
| 🔍 **Deep Trace**        | Interactive AST mapping and semantic node inspection for deep technical insight.              |
| 📊 **Modern Metrics**    | Live Maintainability scores, Complexity index, and Risk Factor detection (Code Smells).       |
| 🌍 **Multi-Language**    | Native support for **Python** and best-effort semantic mapping for **TypeScript/JS**.         |
| 🚀 **Docker Ready**      | Production-grade Dockerization with Vite 7 and FastAPI, optimized for Render/Cloud.           |

---

## 🚀 Quick Start

### Local Development

1. **Clone the project:**

   ```bash
   git clone https://github.com/PhilipTheBackendDeveloper/CodeExplain-AI.git
   cd CodeExplain-AI
   ```

2. **Setup the Engine (Backend):**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   codeexplain serve
   ```

3. **Setup the Dashboard (Frontend):**
   ```bash
   cd ui
   npm install
   npm run dev
   ```

---

## 📖 AI Explanation Modes

CodeExplain adapts to your level of expertise:

- **Beginner (Story Mode)**: 📖 Imagine your code is a storybook. Uses analogies like "Mini-Command Helpers" and "Master Blueprints" to explain functions and classes.
- **Developer**: 🛠️ Technical breakdown with complexity scores, docstring analysis, and structural highlights.
- **Fun: Pirate**: 🏴‍☠️ Arr! Your code explained through the eyes of a salt-crusted sea captain.

---

## 🏗️ Project Structure

```
CodeExplain-AI/
├── core/           # The Brain: AST Cleaners, Explainer Logic (Story Mode), Parsers
├── api/            # Local REST Server (FastAPI)
├── cli/            # Advanced CLI Tooling
├── ui/             # Premium React Dashboard (Vite + Framer Motion)
│   ├── src/        # Dashboard Components & Logic
│   └── public/     # 3D Assets & Logos
├── Dockerfile      # Production Deployment Blueprint
└── requirements.txt
```

---

## ☁️ Deployment

CodeExplain is ready for one-click deployment on platforms like **Render**.

**Docker Build Specs:**

- **Frontend**: Node 20 (Vite 7)
- **Backend**: Python 3.11-slim
- **Port**: 8000

---

## 📜 License

MIT © [Philip The Backend Developer](https://github.com/PhilipTheBackendDeveloper)
