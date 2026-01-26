from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import (supplier_pydantic, supplier_pydanticIn, Supplier)

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

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
