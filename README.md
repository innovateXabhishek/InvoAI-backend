# Invo AI Backend

This repository contains a production‑ready skeleton for **Invo AI**, an
AI‑powered invoice and bill‑processing platform.  The backend is built
with [FastAPI](https://fastapi.tiangolo.com/) to provide a type‑hinted,
high‑performance web API.  Long‑running document parsing and AI
inference are delegated to asynchronous Celery tasks backed by Redis.
The code structure separates concerns into API endpoints, data
schemas, database models and service logic, making it straightforward
to maintain and extend.

## Project structure

```
invo_ai_backend/
├── README.md                — high level description (this file)
├── requirements.txt         — pinned Python dependencies
└── app/
    ├── main.py              — FastAPI application and API routes
    ├── config.py            — configuration management (env vars)
    ├── database.py          — SQLAlchemy session and models base
    ├── models.py            — SQLAlchemy ORM models for invoices
    ├── schemas.py           — Pydantic models for request/response
    ├── services/
    │   └── invoice_extraction.py  — stub for OCR/LLM extraction logic
    └── tasks.py             — Celery tasks for async processing
```

### API design

The API exposes a small set of endpoints that correspond to the core
features of your application:

- `POST /upload` accepts a PDF or JPEG via multipart upload.  The
  endpoint stores the file, registers a new `Invoice` record in the
  database and enqueues a Celery task to extract structured data
  asynchronously.  The response returns the created invoice ID and
  task ID.
- `GET /invoices/{invoice_id}` returns the stored metadata and
  extracted fields for a single invoice.  It optionally waits for the
  associated task to complete when `?wait=true` is passed.
- `GET /invoices` lists recently uploaded invoices, paginated.
- `POST /chat/{invoice_id}` accepts a natural language question about a
  specific invoice and forwards it to your conversational AI layer
  (e.g. using an LLM with retrieval augmented generation).

These endpoints use Pydantic schemas to validate and document their
request and response bodies.  FastAPI automatically generates
OpenAPI/Swagger documentation at `/docs`, which makes the API
self‑describing and easy to integrate.

### Asynchronous processing

Parsing scanned bills involves multiple I/O‑bound operations—reading
large files, calling OCR services and sending prompts to vision
models—which can take several seconds.  To keep API responses
“lightning fast”, heavy work is done off the main request thread.  The
`upload_invoice` endpoint enqueues a `process_invoice` Celery task
defined in `app/tasks.py`.  Once the task finishes it updates the
database with extracted line items, supplier details and totals.

This pattern follows FastAPI’s recommendation: declare path
operations with either `async def` or plain `def` depending on
whether you need `await` inside【841858730467372†L284-L333】.
Tasks that make network or file I/O calls use `async` where
appropriate to leverage Starlette’s event loop for concurrency.

### Data model

Invoices and their line items are stored in a relational database
(PostgreSQL in the example configuration).  SQLAlchemy models in
`models.py` define tables for suppliers, buyers, invoices and
`InvoiceLine`.  The ORM classes allow complex queries and migrations
without writing raw SQL.  Pydantic schemas mirror these models and
provide type safety for API responses.

### Deployment

To run the API locally:

```bash
# Install dependencies in a virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set environment variables (see app/config.py for details)
cp .env.example .env  # edit database and API keys

# Start Redis for Celery tasks (e.g. via Docker)
# This command launches a local Redis instance for development
docker run -p 6379:6379 redis:7

# Run the Celery worker in a separate terminal
celery -A app.tasks worker --loglevel=info

# Launch the FastAPI server (hot reload during development)
uvicorn app.main:app --reload --port 8000
```

FastAPI automatically serves interactive API docs at
`http://localhost:8000/docs`.  In production you should deploy behind
a process manager (e.g. Gunicorn) and use an HTTPS reverse proxy
(e.g. Traefik or Nginx).

### Extending invoice extraction

The file `services/invoice_extraction.py` contains stub functions
`extract_invoice_data` and `ask_about_invoice`.  In a real system,
these would call your OCR engine (Azure Document Intelligence,
Google Document AI, LlamaParse, etc.) to extract raw text and layout
information from PDFs and images.  The extracted content is then
passed to a vision‑capable LLM to produce a structured JSON object
containing supplier details, buyer details, line items and totals.

The asynchronous Celery task uses these service functions so that
errors or timeouts don’t block the main API thread.  You can add
confidence scores, mathematical validations and human review flags to
make the extraction pipeline robust.

### Front‑end integration

Although this repository only covers the backend, your Flutter front
end should follow best practices for a “buttery smooth” experience.  In
2025, Flutter performance guides emphasised keeping widget rebuilds
small, using lazy lists for long scrolling content and compressing
images to reduce memory footprint【999302695344648†L85-L116】【999302695344648†L120-L139】.
Avoid deep widget nesting and move expensive work off the main UI
thread to isolate heavy computation or JSON parsing【999302695344648†L166-L225】.

Flutter packages such as `adaptive_platform_ui` automatically render
native iOS 26 components like Liquid Glass toolbars, spring‑animated
buttons and dynamic colors【74369498187496†L66-L104】, giving your app a
familiar iOS look while preserving Material 3 support on Android.
Combine these packages with a clear, consistent design system to
honour Apple’s Human Interface Guideline principles of **clarity**,
**deference** and **depth**【431482944229062†L155-L160】.

With this backend and a thoughtfully crafted Flutter front end,
Invo AI will deliver an effortless, uninterrupted user experience and
lightning‑fast responses.