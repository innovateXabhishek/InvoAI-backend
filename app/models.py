"""SQLAlchemy ORM models.

These classes define the structure of the database tables used by
Invo AI.  They map suppliers, buyers, invoices and individual line
items to relational database rows.  Relationships between tables are
modelled using SQLAlchemy's ``relationship`` function.
"""

from datetime import date

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    gstin = Column(String, nullable=True)

    invoices = relationship("Invoice", back_populates="supplier")


class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    gstin = Column(String, nullable=True)

    invoices = relationship("Invoice", back_populates="buyer")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=True)
    invoice_no = Column(String, nullable=True)
    invoice_date = Column(Date, default=date.today)
    subtotal = Column(Float, nullable=True)
    tax_total = Column(Float, nullable=True)
    grand_total = Column(Float, nullable=True)
    status = Column(String, default="processing")
    file_path = Column(String, nullable=True)

    supplier = relationship("Supplier", back_populates="invoices")
    buyer = relationship("Buyer", back_populates="invoices")
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    description = Column(String, nullable=True)
    quantity = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    rate = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)
    tax_rate = Column(Float, nullable=True)

    invoice = relationship("Invoice", back_populates="lines")