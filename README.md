# Invo AI Backend - Render Safe Version

This is a minimal FastAPI backend designed to deploy successfully on Render.

## Endpoints

- `GET /` - status
- `GET /health` - health check
- `POST /upload` - upload PDF/JPG/JPEG invoice
- `GET /invoices` - list uploaded invoices
- `GET /invoices/{invoice_id}` - get invoice by ID
- `POST /chat/{invoice_id}` - mock invoice chat

## Render Settings

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Test URL

After deployment, open:

```text
https://your-render-url.onrender.com/docs
```
