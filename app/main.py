from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import uuid
import os

app = FastAPI(
    title="Invo AI Backend",
    version="1.0.0",
    description="Live test backend for invoice and bill upload/extraction."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

INVOICES = {}


@app.get("/")
def root():
    return {
        "app": "Invo AI",
        "status": "live",
        "docs": "/docs",
        "message": "Invo AI backend is running successfully."
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/upload")
async def upload_invoice(file: UploadFile = File(...)):
    allowed_extensions = [".pdf", ".jpg", ".jpeg"]
    filename = file.filename or ""

    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, JPG, and JPEG files are allowed."
        )

    invoice_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{invoice_id}_{filename}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Mock extraction for live testing.
    # Later you can replace this with OpenAI / Azure Document Intelligence / Google Document AI.
    extracted_data = {
        "invoice_id": invoice_id,
        "file_name": filename,
        "file_size_bytes": len(content),
        "status": "processed",
        "supplier": {
            "name": "Demo Supplier",
            "gstin": "Not extracted in mock mode",
            "phone": None,
            "email": None,
            "address": None
        },
        "buyer": {
            "name": "Demo Buyer",
            "gstin": "Not extracted in mock mode",
            "phone": None,
            "address": None
        },
        "items": [
            {
                "description": "Sample item extracted from invoice",
                "quantity": 1,
                "price": 100.0,
                "amount": 100.0
            }
        ],
        "subtotal": 100.0,
        "tax_total": 5.0,
        "grand_total": 105.0,
        "created_at": datetime.utcnow().isoformat()
    }

    INVOICES[invoice_id] = extracted_data
    return extracted_data


@app.get("/invoices")
def list_invoices():
    return {
        "count": len(INVOICES),
        "invoices": list(INVOICES.values())
    }


@app.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: str):
    invoice = INVOICES.get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@app.post("/chat/{invoice_id}")
def chat_with_invoice(invoice_id: str, question: str):
    invoice = INVOICES.get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return {
        "invoice_id": invoice_id,
        "question": question,
        "answer": "This is mock chat mode. The backend is live. Real AI chat can be connected after deployment is stable."
    }
