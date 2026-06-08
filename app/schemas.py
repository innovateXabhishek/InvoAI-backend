from pydantic import BaseModel
from typing import Optional, List


class SupplierOut(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gstin: Optional[str] = None

    class Config:
        orm_mode = True


class BuyerOut(BaseModel):
    name: Optional[str] = None
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
    id:int
    invoice_no: Optional[str]=None
    invoice_date: Optional[str]=None
    subtotal: Optional[float]=None
    tax_total: Optional[float]=None
    grand_total: Optional[float]=None
    status:str

    supplier: Optional[SupplierOut]=None
    buyer: Optional[BuyerOut]=None

    lines: List[LineItem]=[]

    class Config:
        orm_mode = True


class UploadResponse(BaseModel):
    invoice_id:int
    task_id:str


class ChatRequest(BaseModel):
    question:str


class ChatResponse(BaseModel):
    answer:str
