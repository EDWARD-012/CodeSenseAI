# CodeSense AI — AI Code Reviewer & Error Detector

An AI-powered web application that reviews source code, detects bugs, explains problems, and suggests improvements. Built with Django + Ollama.

![CodeSense AI](https://img.shields.io/badge/CodeSense-AI-6C5CE7?style=for-the-badge)
![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)

## Features

- 🔍 **AI Code Review** — Get structured feedback on bugs, security, performance & style
- 💬 **AI Chat** — Ask follow-up questions about your code and reviews
- 📚 **RAG Knowledge Base** — Contextual coding references enhance AI responses
- 🌙 **Dark/Light Theme** — Developer-friendly IDE-like interface
- ⚡ **Multi-Language** — Supports Python, JavaScript, TypeScript, Java, C++, Go, Rust & more

## Quick Start

### Prerequisites

- **Python 3.10+**
- **Ollama** — [Install Ollama](https://ollama.ai)
- A code model pulled in Ollama (e.g., `qwen2.5-coder`)

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd project

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Start Ollama

```bash
# In a separate terminal
ollama pull qwen2.5-coder
ollama serve
```

### 4. Run Django

```bash
python manage.py runserver
```

Open **http://localhost:8000** in your browser.

## Usage

1. **Write/paste code** in the left editor panel
2. **Select language** and **review mode** from the header
3. Click **Review** (or press `Ctrl+Enter`)
4. View results in the **Review Analysis** panel
5. Ask follow-up questions in the **AI Assistant** chat

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/review-code` | Submit code for AI review |
| `POST` | `/api/chat` | Follow-up questions about code |
| `POST` | `/api/run-code` | Reserved (disabled) |

## Project Structure

```
├── api/                   # Django API app
│   ├── services/          # Business logic layer
│   │   ├── ollama_service.py    # Ollama API communication
│   │   ├── prompt_service.py    # Prompt engineering
│   │   ├── rag_service.py       # RAG knowledge retrieval
│   │   └── validation_service.py # Input validation
│   ├── views.py           # API endpoint handlers
│   ├── urls.py            # API routing
│   └── tests.py           # API tests
├── core/                  # Django project config
│   ├── settings.py        # Configuration
│   ├── urls.py            # Root routing
│   └── wsgi.py            # WSGI entry point
├── data/                  # RAG knowledge base
│   ├── rag-docs.json      # Coding knowledge snippets
│   └── code-review-rules.json
├── static/                # Frontend assets
│   ├── css/main.css       # Stitch design system CSS
│   └── js/                # JavaScript modules
├── templates/             # Django HTML templates
│   └── index.html         # Main application page
├── manage.py
├── requirements.txt
└── .env.example
```

## Running Tests

```bash
python manage.py test api
```

## Tech Stack

- **Backend:** Django 6.0, Python
- **Frontend:** HTML, CSS (Stitch Design System), Vanilla JavaScript
- **AI:** Ollama (local LLM inference)
- **RAG:** File-based keyword retrieval

## License

MIT
