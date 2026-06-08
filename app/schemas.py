"""Pydantic schemas for request and response validation.

These classes define the shape of data exchanged via the API.  They
mirror the SQLAlchemy models but omit internal fields (such as
foreign keys) and provide type hints for optional values.  Pydantic
models can be used directly as response models in FastAPI endpoints
to generate accurate OpenAPI documentation.
"""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class SupplierOut(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gstin: Optional[str] = None

    class Config:
        orm_mode = True


class BuyerOut(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    gstin: Optional[str] = None

    class Config:
        orm_mode = True


class LineItem(BaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    rate: Optional[float] = None
    amount: Optional[float] = None
    tax_rate: Optional[float] = None

    class Config:
        orm_mode = True


class InvoiceResponse(BaseModel):
    id: int
    invoice_no: Optional[str] = None
    invoice_date: Optional[date] = None
    subtotal: Optional[float] = None
    tax_total: Optional[float] = None
    grand_total: Optional[float] = None
    status: str
    supplier: Optional[SupplierOut] = None
    buyer: Optional[BuyerOut] = None
    lines: List[LineItem] = []

    class Config:
        orm_mode = True


class UploadResponse(BaseModel):
    invoice_id: int
    task_id: str


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str