"""Celery tasks for Invo AI.

These tasks perform long‑running or network‑bound operations outside
the main FastAPI request thread.  Using Celery allows you to defer
invoice parsing and AI calls without blocking HTTP responses.  This
module defines a single task ``process_invoice`` which reads an
uploaded document from disk, extracts structured data and persists
it to the database.

The Celery worker should be started separately using the command:

```
celery -A app.tasks worker --loglevel=info
```

See ``README.md`` for complete setup instructions.
"""

from __future__ import annotations

import logging
from typing import Optional

from celery import Celery

from .config import settings
from .database import SessionLocal, engine
from .models import Invoice, Supplier, Buyer, InvoiceLine
from .services import invoice_extraction

# Configure Celery.  The broker URL comes from our Pydantic settings.
celery_app = Celery("invo_ai", broker=settings.redis_broker_url)

# You might also set result_backend here if you want to store task
# results.  For demonstration we rely on the database to store
# extracted invoice data, so the default (no result backend) is fine.


@celery_app.task(name="process_invoice")
def process_invoice(invoice_id: int, file_path: str) -> str:
    """Parse an uploaded invoice and persist its data.

    Args:
        invoice_id: Primary key of the invoice record created when
            the user uploaded a document.
        file_path: Absolute path to the uploaded file on disk.  The
            file should remain available until the task completes.

    Returns:
        A short status message.  The extracted data is stored in the
        database rather than returned directly.
    """
    session = SessionLocal()
    try:
        invoice = session.get(Invoice, invoice_id)
        if not invoice:
            logging.error("Invoice %s not found in database", invoice_id)
            return f"invoice {invoice_id} not found"

        # Call the extraction service (stub) to get structured data
        data = invoice_extraction.extract_invoice_data(file_path)

        # Upsert supplier
        supplier_data = data.get("supplier") or {}
        supplier = None
        if supplier_data:
            supplier = Supplier(
                name=supplier_data.get("name"),
                address=supplier_data.get("address"),
                phone=supplier_data.get("phone"),
                email=supplier_data.get("email"),
                gstin=supplier_data.get("gstin"),
            )
            session.add(supplier)
            session.flush()  # get generated ID

        # Upsert buyer
        buyer_data = data.get("buyer") or {}
        buyer = None
        if buyer_data:
            buyer = Buyer(
                name=buyer_data.get("name"),
                address=buyer_data.get("address"),
                phone=buyer_data.get("phone"),
                gstin=buyer_data.get("gstin"),
            )
            session.add(buyer)
            session.flush()

        # Update invoice record
        invoice.supplier_id = supplier.id if supplier else None
        invoice.buyer_id = buyer.id if buyer else None
        invoice.invoice_no = data.get("invoice", {}).get("invoice_no")
        invoice.invoice_date = data.get("invoice", {}).get("invoice_date")
        invoice.subtotal = data.get("totals", {}).get("subtotal")
        invoice.tax_total = data.get("totals", {}).get("tax_total")
        invoice.grand_total = data.get("totals", {}).get("grand_total")
        invoice.status = "completed"
        session.add(invoice)
        session.flush()

        # Insert line items
        lines = data.get("lines", [])
        for line_data in lines:
            line = InvoiceLine(
                invoice_id=invoice.id,
                description=line_data.get("description"),
                quantity=line_data.get("quantity"),
                unit=line_data.get("unit"),
                rate=line_data.get("rate"),
                amount=line_data.get("amount"),
                tax_rate=line_data.get("tax_rate"),
            )
            session.add(line)
        session.commit()
        return "invoice processed"
    except Exception as exc:  # noqa: BLE001
        session.rollback()
        logging.exception("Failed to process invoice %s: %s", invoice_id, exc)
        if invoice := session.get(Invoice, invoice_id):
            invoice.status = "failed"
            session.add(invoice)
            session.commit()
        return f"invoice processing failed: {exc}"
    finally:
        session.close()


# Optionally a task for conversational answering could be defined here
@celery_app.task(name="answer_question")
def answer_question(invoice_id: int, question: str) -> str:
    """Async task to answer a question about an invoice.

    This stub simply fetches the invoice from the database and calls
    ``invoice_extraction.ask_about_invoice`` on the stored data.  In
    reality you might fetch richer context or use retrieval to
    construct a prompt.
    """
    session = SessionLocal()
    try:
        invoice = session.get(Invoice, invoice_id)
        if not invoice:
            return "invoice not found"
        # Build a dict representation of the invoice
        data: dict[str, Optional[object]] = {
            "supplier": {
                "name": invoice.supplier.name if invoice.supplier else None,
                "address": invoice.supplier.address if invoice.supplier else None,
                "phone": invoice.supplier.phone if invoice.supplier else None,
                "email": invoice.supplier.email if invoice.supplier else None,
                "gstin": invoice.supplier.gstin if invoice.supplier else None,
            },
            "buyer": {
                "name": invoice.buyer.name if invoice.buyer else None,
                "address": invoice.buyer.address if invoice.buyer else None,
                "phone": invoice.buyer.phone if invoice.buyer else None,
                "gstin": invoice.buyer.gstin if invoice.buyer else None,
            },
            "invoice": {
                "invoice_no": invoice.invoice_no,
                "invoice_date": invoice.invoice_date,
            },
            "totals": {
                "subtotal": invoice.subtotal,
                "tax_total": invoice.tax_total,
                "grand_total": invoice.grand_total,
            },
            "lines": [
                {
                    "description": l.description,
                    "quantity": l.quantity,
                    "unit": l.unit,
                    "rate": l.rate,
                    "amount": l.amount,
                    "tax_rate": l.tax_rate,
                }
                for l in invoice.lines
            ],
        }
        return invoice_extraction.ask_about_invoice(data, question)
    except Exception as exc:  # noqa: BLE001
        logging.exception("Failed to answer question for invoice %s: %s", invoice_id, exc)
        return "an error occurred"
    finally:
        session.close()