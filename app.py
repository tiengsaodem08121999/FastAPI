from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import (supplier_pydantic, supplier_pydanticIn, Supplier, product_pydanticIn, product_pydantic, Products)

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

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
