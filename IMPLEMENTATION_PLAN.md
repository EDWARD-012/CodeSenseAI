# AI Code Reviewer and Error Detector - Implementation Plan

## 1. Project Overview

### What the App Does

This project is an AI-powered web application that reviews source code, detects likely errors, explains problems, and suggests improvements. Users paste or write code in the browser, submit it for review, and receive structured AI feedback from a Django backend.

The project is designed for a simple Vercel deployment using Django with Vercel's Python runtime. Django is the primary backend framework, while the frontend stays lightweight with HTML, CSS, and JavaScript.

### Key Features

- Browser-based code editor.
- AI code review and error detection.
- Follow-up chat about reviewed code.
- Optional safe `/run-code` endpoint for future sandboxed execution.
- Lightweight RAG support for local coding knowledge.
- Django backend optimized for Vercel deployment.
- Simple static or template-based frontend.
- Ollama integration through the Django services layer.
- Minimal infrastructure and beginner-friendly setup.

---

## 2. Tech Stack

### Frontend

Recommended MVP:

- HTML
- CSS
- Vanilla JavaScript
- Django templates

Optional later upgrade:

- CodeMirror for a richer editor.
- Monaco Editor if a full IDE-like experience is needed.

The MVP should avoid a complex frontend build pipeline unless it becomes necessary.

### Backend

- Django
- Python runtime on Vercel
- Django views for API routes
- Optional Django REST Framework if structured serializers and API tooling are needed

For the MVP, standard Django views returning JSON are enough. Django REST Framework can be added later if the API grows.

### AI

- Ollama API
- Django service module for Ollama requests

Recommended model options:

- `qwen2.5-coder`
- `deepseek-coder`
- `codellama`
- `llama3`

Ollama must run separately from Vercel. The Django app calls Ollama over HTTP.

### RAG

MVP approach:

- File-based local knowledge base.
- JSON or Markdown documents.
- Simple keyword scoring.
- Retrieved snippets injected into the prompt.

Future approach:

- Embeddings.
- Lightweight hosted vector database.
- Django management command for indexing documents.

---

## 3. Folder Structure

Recommended Django structure optimized for Vercel:

```text
/
├── api/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── urls.py
│   ├── views.py
│   ├── schemas.py
│   └── services/
│       ├── __init__.py
│       ├── ollama_service.py
│       ├── prompt_service.py
│       ├── rag_service.py
│       └── validation_service.py
│
├── core/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── frontend/
│   ├── js/
│   │   ├── app.js
│   │   ├── apiClient.js
│   │   ├── editor.js
│   │   ├── chat.js
│   │   └── theme.js
│   └── css/
│       └── main.css
│
├── static/
│   ├── css/
│   ├── js/
│   └── assets/
│       └── logo.svg
│
├── templates/
│   ├── base.html
│   └── index.html
│
├── data/
│   ├── rag-docs.json
│   └── code-review-rules.json
│
├── manage.py
├── requirements.txt
├── vercel.json
├── .env.example
├── .gitignore
└── README.md
```

### Folder and File Responsibilities

#### `/api`

Django app responsible for application routes and backend logic.

- `urls.py`: Defines API routes such as `/review-code`, `/chat`, and `/run-code`.
- `views.py`: Contains Django views that receive requests and return JSON responses.
- `schemas.py`: Optional request and response shape documentation.
- `services/`: Contains the actual business logic so views stay small.

#### `/api/services`

Service layer used by Django views.

- `ollama_service.py`: Calls the external Ollama API.
- `prompt_service.py`: Builds code review and chat prompts.
- `rag_service.py`: Retrieves relevant local knowledge snippets.
- `validation_service.py`: Validates request payloads and input size.

#### `/core`

Main Django project configuration.

- `settings.py`: Django settings, installed apps, static files, environment variables, and Vercel-safe configuration.
- `urls.py`: Root URL configuration that maps frontend pages and API routes.
- `wsgi.py`: WSGI entry point used by Vercel's Python runtime.
- `asgi.py`: ASGI entry point for compatibility, although the MVP can use WSGI.

#### `/frontend`

Source files for frontend CSS and JavaScript before copying or collecting into `/static`.

This folder is useful for organizing frontend source files without adding a frontend framework.

#### `/static`

Static files served by Django and collected for deployment.

- CSS files.
- JavaScript files.
- Images and icons.

#### `/templates`

Django templates rendered by the backend.

- `base.html`: Shared layout.
- `index.html`: Main app page with the editor, review panel, and chat panel.

#### `/data`

Lightweight local RAG data.

- `rag-docs.json`: Local coding knowledge snippets.
- `code-review-rules.json`: Static review rules and categories.

#### Root Files

- `manage.py`: Django command-line entry point.
- `requirements.txt`: Python dependencies for Vercel.
- `vercel.json`: Optional but recommended for explicit routing if needed.
- `.env.example`: Documents required environment variables.
- `.gitignore`: Excludes virtual environments, local env files, caches, and build output.
- `README.md`: Local setup and Vercel deployment guide.

---

## 4. How Django Maps to Vercel

### Vercel Runtime Model

Vercel runs Django using its Python runtime. The Django app is executed in a serverless-style environment, where incoming HTTP requests are routed to the Django application entry point.

The important mapping is:

```text
Vercel request
    -> Python runtime
    -> core/wsgi.py
    -> Django URL resolver
    -> Django view
    -> JSON response or rendered template
```

### Route Handling

Recommended route design:

- `/` renders the main Django template.
- `/review-code` handles code review API requests.
- `/chat` handles follow-up chat requests.
- `/run-code` is reserved for optional future sandboxed execution.
- `/static/...` serves CSS, JavaScript, and assets.

Root URL mapping:

```text
core/urls.py
    -> frontend page route
    -> include api.urls
```

API URL mapping:

```text
api/urls.py
    -> /review-code
    -> /chat
    -> /run-code
```

### Serverless Compatibility Rules

The Django app should be written as a request-response application:

- No long-running local server process.
- No background workers inside the Vercel function.
- No local persistent file writes during requests.
- No dependency on local Ollama running inside the deployment.
- Keep request processing short and predictable.

---

## 5. Vercel Deployment Strategy

### Deployment Goal

The project should deploy on Vercel with minimal configuration:

1. Push the repository to GitHub.
2. Import the repository into Vercel.
3. Set environment variables.
4. Deploy.

### Is `vercel.json` Needed?

Vercel now supports Django with zero-configuration behavior, so `vercel.json` may not be required for a simple Django project.

However, keeping a minimal `vercel.json` can still be useful when:

- Explicit routing is needed.
- The project has custom static handling.
- The default framework detection is not enough.
- Function behavior needs clarification.

Recommendation:

- Start without complex configuration.
- Add `vercel.json` only if route mapping or static handling needs to be explicit.
- If included, keep it minimal.

### Build Behavior

Expected deployment behavior:

- Vercel installs Python dependencies from `requirements.txt`.
- Vercel detects the Python/Django app.
- Django settings are loaded from `core/settings.py`.
- Static files are collected if configured.
- Requests are routed through the Python runtime to Django.

### Start Behavior

There should be no traditional start command like a long-running Gunicorn process.

Vercel handles request execution through its runtime. The Django app should expose the standard WSGI application in `core/wsgi.py`.

### Environment Variables

Required:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`

Optional:

- `ENABLE_RAG`
- `MAX_CODE_CHARS`
- `APP_ENV`
- `REQUEST_TIMEOUT_SECONDS`

Example deployment values:

```text
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=.vercel.app,your-custom-domain.com
OLLAMA_BASE_URL=https://your-ollama-server.example.com
OLLAMA_MODEL=qwen2.5-coder
ENABLE_RAG=true
MAX_CODE_CHARS=20000
```

### Static Files

For the MVP:

- Use Django templates.
- Keep CSS and JavaScript in `/static`.
- Configure Django static settings correctly.
- Run static collection during deployment if needed.

Avoid adding Webpack, Vite, or complex build tooling in the first version.

---

## 6. System Architecture

### Main Request Flow

```text
Browser
    |
    | GET /
    v
Django template view
    |
    | renders index.html
    v
Browser UI
```

### Code Review Flow

```text
Browser frontend
    |
    | fetch('/review-code')
    v
Django view
    |
    | validate payload
    | retrieve optional RAG context
    | build prompt
    v
Ollama service
    |
    | HTTP request to external Ollama server
    v
Ollama model response
    |
    v
Django JSON response
    |
    v
Browser review panel
```

### Layered Backend Design

Use a simple layered structure:

```text
Django view
    -> validation service
    -> RAG service
    -> prompt service
    -> Ollama service
    -> response formatter
```

This keeps the architecture clean without introducing unnecessary infrastructure.

---

## 7. Step-by-Step Implementation Plan

## Phase 1: Django Project Foundation

1. Create the Django project structure.
2. Add `core` project configuration.
3. Add `api` Django app.
4. Add `requirements.txt`.
5. Add `.env.example`.
6. Add `.gitignore`.
7. Add basic `README.md`.
8. Confirm the Django app runs locally.

Goal: A minimal Django app that can render a page and is suitable for Vercel.

## Phase 2: Frontend MVP

1. Create `templates/base.html`.
2. Create `templates/index.html`.
3. Add CSS in `/static/css/main.css`.
4. Add JavaScript in `/static/js/app.js`.
5. Build a simple two-panel interface:
   - Left: code editor.
   - Right: review output and chat.
6. Add language selector.
7. Add review mode selector.
8. Add theme switcher.

Goal: A usable browser interface with no complex frontend build step.

## Phase 3: Code Review API

1. Add `/review-code` route in `api/urls.py`.
2. Add Django view for code review.
3. Validate:
   - Code exists.
   - Code is not too large.
   - Language is supported.
   - Review mode is supported.
4. Build a structured prompt.
5. Call Ollama through the service layer.
6. Return a JSON response.

Goal: Users can submit code and receive AI review feedback.

## Phase 4: Chat API

1. Add `/chat` route.
2. Accept:
   - User message.
   - Current code.
   - Previous review context.
3. Build a follow-up prompt.
4. Call Ollama.
5. Return the answer as JSON.

Goal: Users can ask follow-up questions about code and review results.

## Phase 5: Lightweight RAG

1. Add `/data/rag-docs.json`.
2. Add small reference entries for common coding errors and review guidance.
3. Implement keyword-based retrieval in `rag_service.py`.
4. Retrieve top matching snippets.
5. Inject retrieved context into prompts.
6. Add `ENABLE_RAG` environment variable.

Goal: Improve responses with local reference context while staying deployment-friendly.

## Phase 6: Optional `/run-code`

1. Add the route but keep it disabled by default.
2. Return a clear message that code execution requires a secure sandbox.
3. Do not execute arbitrary code inside Vercel serverless functions.
4. Later, integrate an external sandbox service if needed.

Goal: Preserve the API shape without introducing unsafe behavior.

## Phase 7: Vercel Deployment

1. Push the project to GitHub.
2. Import into Vercel.
3. Configure environment variables.
4. Deploy.
5. Test:
   - `/`
   - `/review-code`
   - `/chat`
6. Confirm Ollama connectivity from the deployed Django app.

Goal: The MVP is live on Vercel and can call an external Ollama endpoint.

---

## 8. API Design

The API can use standard Django views for the MVP. Django REST Framework is optional.

### `POST /review-code`

Purpose:

Reviews submitted code and returns AI-generated feedback.

Request fields:

- `code`: Source code to review.
- `language`: Programming language.
- `reviewMode`: Review type, such as general, bugs, security, or performance.

Response fields:

- `success`: Boolean.
- `summary`: Short review summary.
- `issues`: List of detected issues.
- `suggestions`: List of improvements.
- `riskLevel`: Low, medium, or high.
- `rawResponse`: Optional fallback when the AI response cannot be parsed.

### `POST /chat`

Purpose:

Answers follow-up questions about the submitted code or previous review.

Request fields:

- `message`: User question.
- `code`: Current code context.
- `reviewContext`: Previous review summary or response.

Response fields:

- `success`: Boolean.
- `answer`: AI response.

### `POST /run-code`

Purpose:

Reserved for future code execution.

MVP behavior:

- Keep disabled by default.
- Return a clear message explaining that secure sandboxing is required.

Important:

Do not execute arbitrary user code directly inside Django on Vercel.

---

## 9. UI Plan

### Main Screen

Use a clean split layout:

- Header with app name, language selector, review mode selector, and theme switcher.
- Left panel with code editor.
- Right panel with review results and chat.

### Code Editor

MVP:

- Use a styled `<textarea>`.
- Use a monospace font.
- Support large but bounded input.
- Add placeholder examples.

Later:

- Add CodeMirror.
- Add syntax highlighting.
- Add line numbers.

### Review Output

Display:

- Summary.
- Issues.
- Suggestions.
- Risk level.
- Loading state.
- Error state.

### Chat Panel

Display:

- User questions.
- AI answers.
- Loading state.
- Message input.
- Send button.

### Theme Switcher

Support:

- Light mode.
- Dark mode.
- Persist selected theme with `localStorage`.

---

## 10. Ollama Integration Plan

### Integration Rule

The frontend must not call Ollama directly.

Correct flow:

```text
Frontend fetch
    -> Django endpoint
    -> Ollama service
    -> external Ollama API
    -> Django response
    -> frontend UI
```

### Django to Ollama

The Django service layer calls the Ollama API using `OLLAMA_BASE_URL`.

Supported Ollama endpoints:

- `/api/generate`
- `/api/chat`

The request should include:

- Model name from `OLLAMA_MODEL`.
- Prompt or messages.
- Non-streaming mode for the MVP.
- Timeout settings to avoid hanging serverless requests.

### Local Development

Local workflow:

1. Run Ollama on the developer machine.
2. Pull the chosen model.
3. Set `OLLAMA_BASE_URL` to the local Ollama URL.
4. Run Django locally.
5. Submit code through the web UI.

### Production

Vercel cannot host the Ollama process itself.

Production options:

- Host Ollama on a VPS.
- Host Ollama on a private machine with a secure public tunnel.
- Use a hosted Ollama-compatible API.
- Swap the service layer to another hosted LLM provider later.

Keep `ollama_service.py` isolated so the provider can be changed without rewriting views.

---

## 11. RAG Integration

### MVP RAG Design

Use a file-based knowledge base:

- Store entries in `/data/rag-docs.json`.
- Load entries in `rag_service.py`.
- Match documents using keywords from:
  - User code.
  - Language.
  - Review mode.
  - Chat question.

### Retrieval Flow

```text
Django view
    -> validation service
    -> RAG service
    -> prompt service
    -> Ollama service
```

### Document Shape

Each RAG document should include:

- `id`
- `title`
- `tags`
- `content`

### Scoring

Use simple scoring first:

- Lowercase all text.
- Split into keywords.
- Score by overlap with document title, tags, and content.
- Select the top 3 snippets.

### Why This Is Good for the MVP

- No database required.
- No vector infrastructure required.
- Easy to deploy on Vercel.
- Easy for beginners to understand.
- Enough for small coding reference material.

### Future RAG Upgrade

Later options:

- Ollama embeddings.
- SQLite for local development only.
- Upstash Vector.
- Supabase Vector.
- Neon Postgres with `pgvector`.

For Vercel production, prefer a hosted vector store if the dataset grows.

---

## 12. Frontend Integration

### Recommended Approach

Use Django templates for the first version.

Benefits:

- Minimal setup.
- No frontend build step.
- Easy Vercel deployment.
- Clear beginner-friendly architecture.

### Frontend API Calls

Use browser `fetch` from static JavaScript:

- Submit code to `/review-code`.
- Submit chat messages to `/chat`.
- Handle JSON responses.
- Render results in the page.

### Static Frontend Alternative

If preferred, the app can use a purely static frontend served from Django static files. The frontend still calls the same Django routes.

Recommended MVP choice:

- Django template for the initial page.
- Static JavaScript for interactivity.
- Static CSS for styling.

---

## 13. Performance Considerations

### Cold Starts

Vercel serverless functions may have cold starts. Django has more startup overhead than a tiny serverless function, so the app should keep imports and initialization light.

Recommended practices:

- Avoid expensive module-level work.
- Do not load large models or large datasets inside Django.
- Keep RAG files small.
- Cache small RAG data in memory only after first load.
- Keep dependencies minimal.

### API Latency

AI responses may be slow because the Django app must call an external Ollama server.

Recommended practices:

- Use request timeouts.
- Limit code input size.
- Keep prompts short.
- Use focused review modes.
- Return helpful timeout errors.
- Avoid streaming for the MVP unless Vercel and Django response handling are configured carefully.

### Serverless Constraints

Avoid:

- Long-running background jobs.
- Persistent local file writes.
- In-memory job queues.
- Local subprocesses for user code execution.
- Large dependency trees.
- Heavy startup logic.

---

## 14. Limitations and Workarounds

### Limitation: Serverless Runtime

Vercel is request-based and serverless-style. It is not suitable for long-running Django workers.

Workarounds:

- Keep each endpoint request-response oriented.
- Move background work to external services.
- Avoid Celery or local worker processes in the MVP.

### Limitation: Cold Start Delays

Django may take time to initialize when the function is cold.

Workarounds:

- Keep installed apps minimal.
- Avoid Django REST Framework unless needed.
- Avoid heavy imports at startup.
- Keep RAG data small.

### Limitation: Ollama Cannot Run on Vercel

The Django app can call Ollama, but Vercel should not host the Ollama process.

Workarounds:

- Run Ollama locally for development.
- Host Ollama externally for production.
- Use a hosted LLM provider as a fallback.

### Limitation: Heavy Background Jobs Are Not a Good Fit

Large repository analysis, long code execution, and batch indexing are not ideal inside Vercel serverless requests.

Workarounds:

- Keep the MVP focused on single-snippet review.
- Use external background job platforms later.
- Add GitHub repository review only after introducing job infrastructure.

### Limitation: `/run-code` Is Unsafe Without Sandboxing

Executing arbitrary user code is risky.

Workarounds:

- Keep `/run-code` disabled in the MVP.
- Use static analysis and AI review first.
- Add an external sandbox service later.

---

## 15. Future Improvements

- Add CodeMirror editor.
- Add syntax highlighting.
- Add line numbers.
- Add file upload.
- Add GitHub repository review.
- Add diff-based pull request review.
- Add authentication.
- Add saved review history.
- Add streaming AI responses.
- Add hosted LLM provider fallback.
- Add embeddings-based RAG.
- Add project-specific review rules.
- Add ESLint or parser-based static analysis.
- Add secure external code sandboxing.
- Add background job service for large reviews.

---

## 16. Recommended MVP Scope

Build only the essentials first:

1. Django project with `core` and `api`.
2. Django template frontend.
3. Static CSS and JavaScript.
4. `/review-code` endpoint.
5. `/chat` endpoint.
6. Disabled placeholder `/run-code` endpoint.
7. Ollama service layer.
8. Simple file-based RAG service.
9. Vercel deployment configuration only if needed.

This gives the project the best chance of deploying successfully on Vercel while keeping the architecture clean, understandable, and easy to extend.
