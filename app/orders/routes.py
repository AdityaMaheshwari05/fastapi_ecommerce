from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.deps import get_db
from app.auth.deps import get_current_user
from app.auth.models import User
from app.main import logger
from app.orders import models, schemas
from app.cart.models import Cart
from app.products.models import Product

router = APIRouter()

@router.post("/checkout", response_model=schemas.OrderOut)
def checkout(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.info(f"Checkout started for user {current_user.email}")
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    if not cart_items:
        logger.warning(f"Checkout attempt with empty cart by {current_user.email}")
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0
    order_items = []

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue
        total += product.price * item.quantity
        order_items.append(
            models.OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=product.price
            )
        )

    order = models.Order(
        user_id=current_user.id,
        total_amount=total,
        items=order_items
    )
    db.add(order)

    # Clear cart
    for item in cart_items:
        db.delete(item)

    db.commit()
    db.refresh(order)
    return order

@router.get("/orders", response_model=List[schemas.OrderOut])
def order_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(models.Order).filter(models.Order.user_id == current_user.id).all()

@router.get("/orders/{order_id}", response_model=schemas.OrderOut)
def order_detail(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(models.Order).filter_by(id=order_id, user_id=current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
