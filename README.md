# 🛒 FastAPI E-Commerce Backend

A fully-featured REST API backend for an e-commerce platform, built using **FastAPI** and **PostgreSQL**.

---

## ✅ Features

- User signup/signin with JWT
- Role-based access (admin, user)
- Password reset with token-based security
- Admin product management (CRUD)
- Public product listing, filtering, searching
- Shopping cart (add, update, remove)
- Checkout flow & order history
- Structured error handling with custom format
- Logging via middleware
- API tested via Postman

---

## 🛠 Tech Stack

- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy ORM**
- **Pydantic v2**
- **Passlib** for password hashing
- **Uvicorn** for ASGI server
- **Python 3.11+**

---

## 🚀 Getting Started

### 1. Clone repo and setup virtual environment

```bash
git clone https://github.com/your-username/fastapi-ecommerce.git
cd fastapi-ecommerce
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
