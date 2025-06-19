import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("ecommerce")

from fastapi import FastAPI
from app.core.database import Base, engine

from app.auth.routes import router as auth_router
from app.products.routes import router as admin_product_router
from app.products.public_routes import router as public_product_router
from app.cart.routes import router as cart_router
from app.orders.routes import router as orders_router
from app.cart.models import Cart
from app.auth.models import User
from app.products.models import Product
from app.orders.models import Order, OrderItem

from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.debug(f"Incoming request: {request.method} {request.url}")
        response = await call_next(request)
        logger.debug(f"Response status: {response.status_code}")
        return response

app = FastAPI()
app.add_middleware(LoggingMiddleware)

Base.metadata.create_all(bind=engine)

# Register routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(admin_product_router, prefix="/admin/products", tags=["Admin Product Management"])
app.include_router(public_product_router, prefix="/products", tags=["Public Product APIs"])
app.include_router(cart_router, prefix="/cart", tags=["Cart Management"])
app.include_router(orders_router, tags=["Checkout & Orders"])


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "message": exc.detail, "code": exc.status_code}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": True, "message": "Validation error", "code": 422, "details": exc.errors()}
    )

@app.get("/")
def read_root():
    return {"message": "E-commerce Backend API is running"}
