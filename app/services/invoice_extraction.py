"""Invoice extraction and conversational utilities.

This module contains stub implementations for extracting structured
invoice information from uploaded documents and answering natural
language questions about a processed invoice.  In a production
application you should replace the placeholder logic with calls to
your chosen OCR service (e.g. Azure Document Intelligence, Google
Document AI, LlamaParse) and a vision‑capable LLM such as
OpenAI's GPT‑4o or a self‑hosted model.

The extraction function returns a dictionary keyed by ``supplier``,
``buyer``, ``invoice`` and ``lines``.  Each sub‑dictionary mirrors
the Pydantic schemas defined in ``schemas.py``.  If the parser fails
to recognise a field it should set it to ``None``.  The caller is
responsible for persisting these values to the database.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def extract_invoice_data(file_path: str) -> Dict[str, Any]:
    """Extract structured invoice data from a PDF or image.

    Args:
        file_path: The absolute path to the uploaded document on
            disk.  The file may be a scanned JPEG/PNG or a PDF.

    Returns:
        A nested dictionary with top‑level keys:

        - ``supplier``: Dict with keys ``name``, ``address``, ``phone``,
          ``email`` and ``gstin``.
        - ``buyer``: Dict with the same keys as ``supplier``.
        - ``invoice``: Dict with keys ``invoice_no`` and ``invoice_date``.
        - ``totals``: Dict with ``subtotal``, ``tax_total`` and
          ``grand_total``.
        - ``lines``: List of line item dicts.  Each entry should
          include ``description``, ``quantity``, ``unit``, ``rate``,
          ``amount`` and ``tax_rate``.

    Note:
        This function currently returns a hard‑coded example to
        illustrate the schema expected by the downstream Celery task.
        Replace it with your own extraction pipeline.
    """
    # TODO: implement real OCR + LLM extraction here
    # For demonstration we return dummy data
    return {
        "supplier": {
            "name": "Example Supplier Pty Ltd",
            "address": "123 Example St, Springfield",
            "phone": "1800 555 010",
            "email": "info@example.com",
            "gstin": "22AAAAA0000A1Z5",
        },
        "buyer": {
            "name": "Example Buyer Inc.",
            "address": "456 Buyer Rd, Shelbyville",
            "phone": "1800 555 020",
            "gstin": "33BBBBB1111B2Z6",
        },
        "invoice": {
            "invoice_no": "INV‑001",
            "invoice_date": "2026-06-07",
        },
        "totals": {
            "subtotal": 1000.0,
            "tax_total": 50.0,
            "grand_total": 1050.0,
        },
        "lines": [
            {
                "description": "Item A",
                "quantity": 10,
                "unit": "pcs",
                "rate": 50.0,
                "amount": 500.0,
                "tax_rate": 5.0,
            },
            {
                "description": "Item B",
                "quantity": 5,
                "unit": "pcs",
                "rate": 100.0,
                "amount": 500.0,
                "tax_rate": 5.0,
            },
        ],
    }


def ask_about_invoice(data: Dict[str, Any], question: str) -> str:
    """Answer a natural language question about an invoice.

    Args:
        data: The structured invoice data as returned by
            ``extract_invoice_data``.  In a production system you
            might instead pass an invoice ID and fetch the data
            directly from your database.
        question: The user’s question expressed in natural language.

    Returns:
        A string containing the model’s answer.  The current
        implementation simply echoes the question and returns a
        generic response.  Replace this with a call to your
        conversational AI service.
    """
    # TODO: integrate conversational AI here
    # For now return a canned response
    return (
        "This is a demo response. I don't have a real conversational "
        "model integrated yet. You asked: '{question}'."
    ).format(question=question)