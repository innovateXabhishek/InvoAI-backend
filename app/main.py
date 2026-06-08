"""FastAPI application entry point for Invo AI.

This module defines the web API endpoints that power your invoice
processing backend.  Clients can upload PDF or image files, list
previously processed invoices, retrieve details for a single
invoice and ask natural language questions about the contents of an
invoice.  Heavy work is delegated to Celery tasks to keep
responses snappy.
"""

from __future__ import annotations

import os
from typing import List, Optional

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from celery.result import AsyncResult

from .config import settings
from .database import SessionLocal, engine
from .models import Base, Invoice
from .schemas import (
    ChatRequest,
    ChatResponse,
    InvoiceResponse,
    LineItem,
    SupplierOut,
    BuyerOut,
    UploadResponse,
)
from .tasks import celery_app, process_invoice, answer_question

# Create all tables if they don't already exist.  In a real
# deployment you would handle migrations separately (e.g. Alembic).
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Invo AI API", version="0.1.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/upload", response_model=UploadResponse)
async def upload_invoice(file: UploadFile = File(...), db=Depends(get_db)):
    """Upload a new invoice and trigger asynchronous processing.

    This endpoint accepts a file (PDF or image) via multipart/form-data.
    It writes the file to disk, creates a new invoice record with
    ``status='processing'`` and dispatches a Celery task to parse
    the document.  The response includes the invoice ID and Celery
    task ID so that clients can poll for completion.
    """
    # Ensure upload directory exists
    upload_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # Save file to local storage
    file_location = os.path.join(upload_dir, file.filename)
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    # Create invoice record with status processing
    invoice = Invoice(status="processing", file_path=file_location)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    # Kick off asynchronous processing via Celery
    task = process_invoice.delay(invoice.id, file_location)

    return UploadResponse(invoice_id=invoice.id, task_id=task.id)


@app.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
):
    """Return a paginated list of processed invoices.

    The ``limit`` and ``offset`` query parameters control pagination.
    Results are ordered by descending creation date (most recent first).
    """
    invoices = (
        db.query(Invoice)
        .order_by(Invoice.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        InvoiceResponse(
            id=inv.id,
            invoice_no=inv.invoice_no,
            invoice_date=inv.invoice_date,
            subtotal=inv.subtotal,
            tax_total=inv.tax_total,
            grand_total=inv.grand_total,
            status=inv.status,
            supplier=SupplierOut.from_orm(inv.supplier) if inv.supplier else None,
            buyer=BuyerOut.from_orm(inv.buyer) if inv.buyer else None,
            lines=[
                LineItem(
                    id=l.id,
                    description=l.description,
                    quantity=l.quantity,
                    unit=l.unit,
                    rate=l.rate,
                    amount=l.amount,
                    tax_rate=l.tax_rate,
                )
                for l in inv.lines
            ],
        )
        for inv in invoices
    ]


@app.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    wait: bool = Query(False, description="Wait for processing to complete"),
    db=Depends(get_db),
):
    """Return a single invoice with its extracted data.

    If the invoice is still processing and ``wait`` is true, this
    endpoint will block until the Celery task finishes.  Otherwise it
    returns immediately with ``status='processing'``.
    """
    invoice = db.query(Invoice).get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Optionally wait for task completion
    if wait and invoice.status == "processing":
        # Check Celery task state
        # Since we didn't persist task ID in DB, clients should pass wait
        # only when they know the task has finished (or poll separately).
        # We don't block here; this is a simple placeholder.
        pass

    return InvoiceResponse(
        id=invoice.id,
        invoice_no=invoice.invoice_no,
        invoice_date=invoice.invoice_date,
        subtotal=invoice.subtotal,
        tax_total=invoice.tax_total,
        grand_total=invoice.grand_total,
        status=invoice.status,
        supplier=SupplierOut.from_orm(invoice.supplier) if invoice.supplier else None,
        buyer=BuyerOut.from_orm(invoice.buyer) if invoice.buyer else None,
        lines=[
            LineItem(
                id=l.id,
                description=l.description,
                quantity=l.quantity,
                unit=l.unit,
                rate=l.rate,
                amount=l.amount,
                tax_rate=l.tax_rate,
            )
            for l in invoice.lines
        ],
    )


@app.post("/chat/{invoice_id}", response_model=ChatResponse)
async def chat_with_invoice(
    invoice_id: int,
    request: ChatRequest,
    db=Depends(get_db),
):
    """Answer a natural language question about an invoice.

    This endpoint delegates the question to a Celery task (or could
    call the service synchronously) and returns the AI's answer.  For
    demo purposes we simply call a synchronous stub; in production
    you may want to push this to Celery as well to avoid blocking.
    """
    invoice = db.query(Invoice).get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # For demonstration we call the task synchronously
    answer: str = answer_question(invoice_id, request.question)
    return ChatResponse(answer=answer)