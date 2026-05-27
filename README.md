# 🚀 CodeSense AI — AI Code Reviewer & Error Detector

<p align="center">
  <img src="https://img.shields.io/badge/CodeSense-AI-6C5CE7?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Vercel-Serverless-black?style=for-the-badge&logo=vercel" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
</p>

<p align="center">
  <b>An AI-powered web application that reviews source code, detects bugs, explains problems, and suggests improvements.</b>
</p>

---

## 🌐 Live Demo

🔗 https://shubhamcodeai.vercel.app

---

# ✨ Features

* 🔍 **AI Code Review**
  Get structured feedback on bugs, security, performance, and code quality using **Llama 3.1 70B**.

* 💬 **AI Chat Assistant**
  Ask follow-up questions about your code, reviews, and optimizations.

* ⚡ **Live Code Execution**
  Run code directly in the browser using **Judge0 API**.

* 🪟 **LeetCode Style Interface**
  Resizable split-pane layout with Monaco Editor and terminal output.

* 🌙 **Dark/Light Theme**
  Modern responsive UI with theme switching support.

* ☁️ **Vercel Ready**
  Optimized for serverless deployment on Vercel.

---

# 🛠️ Tech Stack

| Category       | Technology                     |
| -------------- | ------------------------------ |
| Backend        | Django 6.0, Python             |
| Frontend       | Vanilla JS, CSS, Monaco Editor |
| AI Model       | Llama 3.1 70B                  |
| AI API         | Nvidia NIM API                 |
| Code Execution | Judge0 CE API                  |
| Deployment     | Vercel                         |
| Static Files   | WhiteNoise                     |

---

# 🏗️ System Architecture

```text
                ┌─────────────────┐
                │     Frontend    │
                │ Monaco Editor UI│
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   Django API    │
                └──────┬──────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
┌─────────────────┐         ┌─────────────────┐
│ Nvidia NIM API  │         │   Judge0 API    │
│ AI Code Review  │         │ Code Execution  │
└─────────────────┘         └─────────────────┘
```

---

# 📸 Screenshots
## 🔍 AI Review + Code Execution
<img width="1919" height="912" alt="Screenshot 2026-05-27 142500" src="https://github.com/user-attachments/assets/f6ab7dc0-c4a1-48af-9a35-25d166520de5" />

---

# 🚀 Getting Started

## 📋 Prerequisites

* Python 3.10+
* Git
* Nvidia API Key

Get your free Nvidia API key from:

👉 https://build.nvidia.com

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/shubhamjrd4559-sudo/CodeSenseAI.git
cd CodeSenseAI
```

---

## 2️⃣ Create Virtual Environment

### Linux / Mac

```bash
python -m venv venv
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root:

```env
NVIDIA_API_KEY="nvapi-your-key-here"
LLM_MODEL="meta/llama-3.1-70b-instruct"
```

---

# ▶️ Run the Project

```bash
python manage.py runserver
```

Open:

```text
http://localhost:8000
```

---

# ☁️ Deployment on Vercel

This project is pre-configured for serverless deployment using `vercel.json`.

## Deployment Steps

1. Push your project to GitHub
2. Import the repository into Vercel
3. Add environment variables:

   * `NVIDIA_API_KEY`
   * `LLM_MODEL`
4. Click **Deploy**

Done ✅

---

# 🎮 Usage

1. Paste/write code in the editor
2. Select programming language
3. Click **Review** for AI analysis
4. Click **Run** to execute code
5. View output in terminal panel

### Shortcuts

| Action      | Shortcut       |
| ----------- | -------------- |
| Review Code | `Ctrl + Enter` |
| Run Code    | `F5`           |

---

# 📁 Project Structure

```text
CodeSenseAI/
│
├── api/
├── core/
├── templates/
├── static/
├── staticfiles/
├── data/
├── requirements.txt
├── manage.py
├── vercel.json
└── README.md
```

---

# 🔥 Key Highlights

✅ AI-Powered Code Review
✅ Real-Time Code Execution
✅ Serverless Deployment
✅ Professional IDE Experience
✅ Multi-Language Support
✅ Responsive UI

---

# 🚀 Future Improvements

* User Authentication
* Save Review History
* Docker Support
* GitHub Integration
* AI Auto-Fix Suggestions
* Multi-file Analysis

---

# 🤝 Contributing

Contributions are welcome!

```bash
git checkout -b feature-name
git commit -m "Added new feature"
git push origin feature-name
```

Then open a Pull Request 🚀

---

# 📝 License

This project is licensed under the **MIT License**.

---

# 👨‍💻 Author

## Shubham Kumar

* GitHub: https://github.com/shubhamjrd4559-sudo
* Live Project: https://shubhamcodeai.vercel.app

---

# ⭐ Support

If you like this project:

🌟 Star the repository
🍴 Fork the repository
📢 Share with others

---
