from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.auth.deps import get_db
from app.products import models, schemas

router = APIRouter()

@router.get("/", response_model=list[schemas.ProductOut])
def list_products(
    db: Session = Depends(get_db),
    category: str = None,
    min_price: float = 0,
    max_price: float = float("inf"),
    sort_by: str = Query("id", enum=["id", "price", "name"]),
    page: int = 1,
    page_size: int = 10
):
    query = db.query(models.Product)

    if category:
        query = query.filter(models.Product.category == category)

    query = query.filter(models.Product.price >= min_price)
    query = query.filter(models.Product.price <= max_price)

    if sort_by == "price":
        query = query.order_by(models.Product.price)
    elif sort_by == "name":
        query = query.order_by(models.Product.name)
    else:
        query = query.order_by(models.Product.id)

    return query.offset((page - 1) * page_size).limit(page_size).all()

@router.get("/search", response_model=list[schemas.ProductOut])
def search_products(keyword: str, db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.name.ilike(f"%{keyword}%")).all()

@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
