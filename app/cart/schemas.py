from pydantic import BaseModel

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemOut(CartItemCreate):
    id: int

    class Config:
        orm_mode = True
