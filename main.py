from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
import random
from faker import Faker
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
fake = Faker('it_IT')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Define LineItemOrder and LineItemInvoice
class LineItemOrder(BaseModel):
    article: int
    quantity: int
    price: float
    requested_delivery_date: date

class LineItemInvoice(BaseModel):
    article: int
    quantity: int
    price: float
    requested_delivery_date: date
    order_reference: LineItemOrder

# Define Order and Invoice models
class Order(BaseModel):
    order_id: int
    company_name: str
    total_order: float
    order_date: date
    shipping_address: str
    line_items: List[LineItemOrder]

class Invoice(BaseModel):
    invoice_id: int
    company_name: str
    total_amount: float
    invoice_date: date
    shipping_address: str
    scaduto: bool
    line_items: List[LineItemInvoice]

# Generate sample orders and invoices
orders = []
invoices = []

def generate_orders(num_companies: int, orders_per_company: int):
    global orders
    order_id = 1
    for _ in range(num_companies):
        company_name = fake.company()
        for _ in range(orders_per_company):
            righe =[LineItemOrder(
                    article=random.randint(1000, 9999),
                    quantity=random.randint(1, 20),
                    price=round(random.uniform(10, 200), 2),
                    requested_delivery_date=fake.date_between(start_date='today', end_date='+90d')
                ) for _ in range(random.randint(2, 10))]
            order = Order(
                order_id=order_id,
                company_name=company_name,
                total_order=sum(c.price*c.quantity for c in righe),
                order_date=fake.date_between(start_date='-1y', end_date='today'),
                shipping_address=fake.address().replace("\n", ", "),
                line_items=righe
            )
            orders.append(order)
            order_id += 1

def generate_invoices_from_orders(invoices_per_order: int):
    global invoices
    invoice_id = 1
    for order in orders:
        for _ in range(invoices_per_order):
            scaduto = random.choice([True, False])
            righe = [LineItemInvoice(
                    article=item.article,
                    quantity=item.quantity,
                    price=item.price,
                    requested_delivery_date=item.requested_delivery_date,
                    order_reference=item
                ) for item in order.line_items]
            invoice = Invoice(
                invoice_id=invoice_id,
                company_name=order.company_name,
                total_amount=sum(c.price*c.quantity for c in righe),
                invoice_date=fake.date_between(start_date=order.order_date, end_date='+30d'),
                shipping_address=order.shipping_address,
                scaduto=scaduto,
                line_items=righe
            )
            invoices.append(invoice)
            invoice_id += 1

# Populate data
generate_orders(num_companies=10, orders_per_company=5)
generate_invoices_from_orders(invoices_per_order=1)

# 1. API to return all orders, filterable by customer (company_name)
@app.get("/orders", response_model=List[Order])
def get_orders(company_name: Optional[str] = None):
    filtered_orders = orders
    if company_name:
        filtered_orders = [order for order in orders if company_name.lower() in order.company_name.lower()]
    
    if not filtered_orders:
        raise HTTPException(status_code=404, detail="No orders found")
    
    return filtered_orders

# 2. API to return all order line items, filterable by customer, article, and order_id
@app.get("/order-lines", response_model=List[LineItemOrder])
def get_order_lines(
    company_name: Optional[str] = None,
    article: Optional[int] = None,
    order_id: Optional[int] = None
):
    order_lines = []
    filtered_orders = orders
    if company_name:
        filtered_orders = [order for order in orders if company_name.lower() in order.company_name.lower()]
    if order_id:
        filtered_orders = [order for order in filtered_orders if order.order_id == order_id]
    
    for order in filtered_orders:
        for line_item in order.line_items:
            if article is None or line_item.article == article:
                order_lines.append(line_item)
    
    if not order_lines:
        raise HTTPException(status_code=404, detail="No order lines found")
    
    return order_lines

# 3. API to return all invoices, filterable by customer, date, and if expired (scaduto)
@app.get("/invoices", response_model=List[Invoice])
def get_invoices(
    company_name: Optional[str] = None,
    invoice_date: Optional[date] = None,
    scaduto: Optional[bool] = None,
    invoice_id: Optional[int] = None
):
    filtered_invoices = invoices
    if company_name:
        filtered_invoices = [invoice for invoice in invoices if company_name.lower() in invoice.company_name.lower()]
    if invoice_date:
        filtered_invoices = [invoice for invoice in filtered_invoices if invoice.invoice_date == invoice_date]
    if invoice_id:
        filtered_invoices = [invoice for invoice in filtered_invoices if invoice.invoice_id == invoice_id]
    
    if scaduto is not None:
        filtered_invoices = [invoice for invoice in filtered_invoices if invoice.scaduto == scaduto]
    
    if not filtered_invoices:
        raise HTTPException(status_code=404, detail="No invoices found")
    
    return filtered_invoices

# 4. API to return all invoice line items, filterable by customer, article, order_id, and invoice_id
@app.get("/invoice-lines", response_model=List[LineItemInvoice])
def get_invoice_lines(
    company_name: Optional[str] = None,
    article: Optional[int] = None,
    order_id: Optional[int] = None,
    invoice_id: Optional[int] = None
):
    invoice_lines = []
    filtered_invoices = invoices
    if company_name:
        filtered_invoices = [invoice for invoice in invoices if company_name.lower() in invoice.company_name.lower()]
    if invoice_id:
        filtered_invoices = [invoice for invoice in filtered_invoices if invoice.invoice_id == invoice_id]

    for invoice in filtered_invoices:
        for line_item in invoice.line_items:
            if (article is None or line_item.article == article) and (order_id is None or line_item.order_reference.article == order_id):
                invoice_lines.append(line_item)
    
    if not invoice_lines:
        raise HTTPException(status_code=404, detail="No invoice lines found")
    
    return invoice_lines
