# CodeSense AI — AI Code Reviewer & Error Detector

An AI-powered web application that reviews source code, detects bugs, explains problems, and suggests improvements. Built with Django, Nvidia NIM (Llama 3.1 70B), and Judge0 for remote code execution. Ready for Serverless deployment on Vercel.

![CodeSense AI](https://img.shields.io/badge/CodeSense-AI-6C5CE7?style=for-the-badge)
![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)

## Features

- 🔍 **AI Code Review** — Get structured feedback on bugs, security, performance & style using Llama 3.1 70B.
- 💬 **AI Chat** — Ask follow-up questions about your code and reviews.
- ⚡ **Live Code Execution** — Run code directly in the browser (Python, C++, Java, JS, etc.) via Judge0 API.
- 🪟 **LeetCode Style UI** — Fully resizable, split-pane layout with independent scrolling and Monaco Editor.
- 🌙 **Dark/Light Theme** — Developer-friendly modern interface.
- ☁️ **Vercel Ready** — Designed to be deployed effortlessly on Vercel as Serverless Functions.

## Tech Stack

- **Backend:** Django 6.0, Python
- **Frontend:** Vanilla JS, CSS (Stitch Design System), Monaco Editor
- **AI Inference:** Nvidia NIM API (`meta/llama-3.1-70b-instruct`)
- **Code Execution:** Judge0 CE API

## Quick Start (Local Setup)

### Prerequisites

- **Python 3.10+**
- Free **Nvidia API Key** from [build.nvidia.com](https://build.nvidia.com)

### 1. Clone & Install

```bash
git clone https://github.com/shubhamjrd4559-sudo/CodeSenseAI.git
cd CodeSenseAI

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the root directory and add your Nvidia API Key:

```env
NVIDIA_API_KEY="nvapi-your-key-here"
LLM_MODEL="meta/llama-3.1-70b-instruct"
```

### 3. Run Django

```bash
python manage.py runserver
```

Open **http://localhost:8000** in your browser.

## Deployment (Vercel)

This project is pre-configured with `vercel.json` and `wsgi.py` optimizations for 1-click serverless deployment.

1. Push your code to a GitHub repository.
2. Sign in to [Vercel](https://vercel.com) and click **Add New Project**.
3. Import your repository.
4. In the **Environment Variables** section, add:
   - `NVIDIA_API_KEY`: Your Nvidia API key
   - `LLM_MODEL`: `meta/llama-3.1-70b-instruct`
5. Click **Deploy**.

## Usage

1. **Write/paste code** in the right-side editor panel.
2. **Select language** and **review mode** from the top header.
3. Click **Review** (or `Ctrl+Enter`) to get AI analysis on the left panel.
4. Click **Run** (or `F5`) to execute the code and view the output in the bottom terminal.
5. Drag the borders between panels to resize the layout to your preference.

## License

MIT
