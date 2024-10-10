from fastapi import FastAPI, Query, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
import random
from faker import Faker
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader

app = FastAPI()
fake = Faker('it_IT')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "mysecretapikey"  # La tua API Key segreta
API_KEY_NAME = "X-API-Key"  # Nome dell'header da utilizzare per l'API Key
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Funzione per verificare l'API Key
async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

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

# 1. API to return all orders, protected by API key
@app.get("/orders", response_model=List[Order])
def get_orders(api_key: str = Depends(get_api_key)):  
    return orders

# 3. API to return all invoices, protected by API key
@app.get("/invoices", response_model=List[Invoice])
def get_invoices(api_key: str = Depends(get_api_key)):
    return invoices
