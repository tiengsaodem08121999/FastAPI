import email
from email.mime import message
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import (supplier_pydantic, supplier_pydanticIn, Supplier, product_pydanticIn, product_pydantic, Products)

#email:
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form
from starlette.responses import JSONResponse
from starlette.requests import Request
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from pydantic import EmailStr
from pydantic import EmailStr, BaseModel
from typing import List

#docenv
import os
from dotenv import load_dotenv

# Load .env file if exists (for local development)
# In Docker, environment variables are already set by docker-compose
load_dotenv()

#credentials
credentials = {
    'EMAIL': os.getenv('EMAIL', ''),
    'PASSWORD': os.getenv('PASSWORD', '')
}

app = FastAPI()

@app.get("/")
def index():
    return {"Msg": "go to /docs for api documentation"}

@app.post("/supplier/")
async def add_supplier(supplier_info: supplier_pydanticIn):
    supplier_obj = await Supplier.create(**supplier_info.dict(exclude_unset=True))
    repsonse = await supplier_pydantic.from_tortoise_orm(supplier_obj)
    return {"status": "success", "data": repsonse}

@app.get("/suppliers")
async def get_all_suppliers():
    suppliers = await supplier_pydantic.from_queryset(Supplier.all())
    return {"status": "success", "data": suppliers}

@app.get("/supplier/{supplier_id}")
async def get_supplier(supplier_id: int):
    supplier = await supplier_pydantic.from_queryset_single(Supplier.get(id=supplier_id))
    return {"status": "success", "data": supplier}

@app.put("/supplier/{supplier_id}")
async def update_supplier(supplier_id: int, supplier_info: supplier_pydanticIn):
    await Supplier.filter(id=supplier_id).update(**supplier_info.dict(exclude_unset=True))
    supplier = await supplier_pydantic.from_queryset_single(Supplier.get(id=supplier_id))
    return {"status": "success", "data": supplier}

@app.delete("/supplier/{supplier_id}")
async def delete_supplier(supplier_id: int):
    deleted_count = await Supplier.filter(id=supplier_id).delete()
    if not deleted_count:
        return {"status": "error", "message": f"Supplier with id {supplier_id} not found"}
    return {"status": "success", "message": f"Deleted supplier with id {supplier_id}"}

@app.post("/products/{supplier_id}")
async def add_product_to_supplier(supplier_id: int, product_details: product_pydanticIn):
    supplier = await Supplier.get(id=supplier_id)
    product_details = product_details.dict(exclude_unset=True)
    product_details['revenue'] += product_details['quantity_sold'] * product_details['unit_price']
    product_obj = await Products.create(**product_details, supplied_by = supplier)
    repsonse = await product_pydantic.from_tortoise_orm(product_obj)
    return {"status": "success", "data": repsonse}
    
@app.get("/products")
async def get_all_products():
    products = await product_pydantic.from_queryset(Products.all())
    return {"status": "success", "data": products}

@app.get("/product/{product_id}")
async def get_product(product_id: int):
    product = await product_pydantic.from_queryset_single(Products.get(id=product_id))
    return {"status": "success", "data": product}

@app.put("/product/{product_id}")
async def update_product(id: int, update_info:product_pydantic):
    product = await Products.get(id=id)
    update_info = update_info.dict(exclude_unset=True)
    product.name = update_info['name']
    product.quantity_in_stock = update_info['quantity_in_stock']
    product.quantity_sold += update_info['quantity_sold']
    product.revenue += update_info['quantity_sold'] * update_info['unit_price']
    product.unit_price = update_info['unit_price']
    await product.save()
    reposnse = await product_pydantic.from_tortoise_orm(product)
    return {"status": "success", "data": reposnse}

@app.delete("/product/{product_id}")
async def delete_product(product_id: int):
    deleted_count = await Products.filter(id=product_id).delete()
    if not deleted_count:
        return {"status": "error", "message": f"Product with id {product_id} not found"}
    return {"status": "success", "message": f"Deleted product with id {product_id}"}

class EmailSchema(BaseModel):
    email: List[EmailStr]

class EmailContent(BaseModel):
    message: str
    subject: str

conf = ConnectionConfig(
    MAIL_USERNAME = credentials['EMAIL'],
    MAIL_PASSWORD = credentials['PASSWORD'],
    MAIL_FROM = credentials['EMAIL'],
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS=True,   # ✅ thay cho MAIL_TLS
    MAIL_SSL_TLS=False,  # ✅ thay cho MAIL_SSL
)

@app.post("/email/{product_id}")
async def send_email(product_id: int, content: EmailContent):

    product = await Products.get(id=product_id)
    supplier = await product.supplied_by
    supplier_email = [supplier.email]

    html = """
        <h5>John Doe,</h5>
        <p>We would like to inform you about the latest update regarding our product with ID: {product_id}.</p>
        </br>
        <p>{content.subject}</p>
        </br>
        <p>{content.message}</p>
        </br>
        <h6>Best regards,</h6>
        <h6>John's Company</h6>
    """

    message = MessageSchema(
        subject= content.subject,
        recipients=supplier_email,
        body=html,
        subtype="html"
        )
    fm = FastMail(conf)
    await fm.send_message(message)
    return {"status": "success", "message": f"Email sent to supplier of product id {product_id}"}

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
