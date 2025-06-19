from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.cart import models, schemas
from app.products.models import Product
from app.auth.deps import get_db, get_current_user
from app.auth.models import User

router = APIRouter()

@router.post("/", response_model=schemas.CartItemOut)
def add_to_cart(
    item: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = db.query(models.Cart).filter_by(user_id=current_user.id, product_id=item.product_id).first()

    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = models.Cart(
            user_id=current_user.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.get("/", response_model=list[schemas.CartItemOut])
def view_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(models.Cart).filter(models.Cart.user_id == current_user.id).all()

@router.put("/{product_id}", response_model=schemas.CartItemOut)
def update_quantity(
    product_id: int,
    item: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_item = db.query(models.Cart).filter_by(user_id=current_user.id, product_id=product_id).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not in cart")

    cart_item.quantity = item.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.delete("/{product_id}")
def remove_from_cart(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_item = db.query(models.Cart).filter_by(user_id=current_user.id, product_id=product_id).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}
