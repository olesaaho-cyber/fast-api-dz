from typing import Optional

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field

app = FastAPI(title="HW6 FastAPI Service")


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    description: Optional[str] = None


class Item(ItemCreate):
    id: int


items: dict[int, Item] = {}
next_id = 1


@app.get("/")
def root():
    return {"message": "HW6 FastAPI service is running"}


# QUERY-параметры: limit, offset, q
@app.get("/items")
def list_items(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None, min_length=1),
):
    result = list(items.values())

    if q:
        result = [item for item in result if q.lower() in item.name.lower()]

    return {
        "total": len(result),
        "items": result[offset: offset + limit],
    }


# PATH-параметр: item_id, QUERY-параметр: verbose
@app.get("/items/{item_id}")
def get_item(
    item_id: int = Path(..., ge=1),
    verbose: bool = Query(False),
):
    item = items.get(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if verbose:
        return {"item": item, "source": "memory"}

    return item


# POST + BODY-параметр
@app.post("/items", status_code=201)
def create_item(item: ItemCreate):
    global next_id

    new_item = Item(id=next_id, **item.model_dump())
    items[next_id] = new_item
    next_id += 1

    return new_item


# PUT + PATH + BODY
@app.put("/items/{item_id}")
def update_item(item: ItemCreate, item_id: int = Path(..., ge=1)):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")

    updated = Item(id=item_id, **item.model_dump())
    items[item_id] = updated

    return updated