# Medicine Inventory & Order API 💊

A high-performance, asynchronous RESTful API built with **FastAPI** and **MongoDB (Motor)** for managing pharmaceutical medicine inventory, processing orders with atomic stock validation, and securing administrative write operations via **JWT authentication**.

---

## 🚀 Key Features & Highlights

- **⚡ Asynchronous Architecture**: Fully async request pipeline using FastAPI and Motor (async MongoDB driver).
- **🔒 JWT Authentication & Authorization**: Secure user registration, password hashing with `bcrypt`, and Bearer JWT token validation. Public catalog browsing with protected mutation endpoints.
- **📦 Atomic Stock Decrement & Concurrency Control**: Order processing validates stock and atomically updates inventory using MongoDB conditional updates (`{"$gte": qty}`) to prevent race conditions and overselling.
- **🔍 Case-Insensitive Catalog Search**: Regex partial matching for substring searches on medicine names, backed by startup index creation.
- **⚡ Automated Database Indexing**: Lifecycle-managed indexing on `medicines.name`, `medicines.category`, and unique index on `users.username`.
- **🛡️ Robust Error Handling & Validation**: Pydantic v2 data models with strict constraint validation (`gt`, `ge`, `min_length`) and a global 500 exception handler that prevents sensitive stack trace leaks.
- **🐳 Docker & Docker Compose Ready**: Multi-container setup orchestrating the FastAPI application and MongoDB service.

---

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: MongoDB & Motor (Async Python Driver)
- **Data Validation & Settings**: Pydantic v2, Pydantic-Settings
- **Security & Auth**: `python-jose` (JWT), `bcrypt`
- **Server**: Uvicorn (ASGI)
- **Containerization**: Docker, Docker Compose

---

## 📁 Project Structure

```text
medicine-inventory-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entrypoint, lifespan, global exception handler
│   ├── config.py            # Environment configuration & JWT settings (BaseSettings)
│   ├── database.py          # Async Motor client & startup indexing logic
│   ├── auth/
│   │   ├── __init__.py
│   │   └── security.py      # Password hashing, JWT token creation, get_current_user dependency
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── medicines.py     # Medicine database operations & regex partial search
│   │   ├── orders.py        # Order creation, atomic stock decrement & verification
│   │   └── users.py         # User retrieval and registration operations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── medicine.py      # Medicine schemas (MedicineCreate, MedicineOut)
│   │   ├── order.py         # Order schemas (OrderItem, OrderCreate, OrderOut)
│   │   └── user.py          # User schemas (UserCreate, UserLogin, UserOut, Token)
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # /auth/register and /auth/login endpoints
│       ├── medicines.py     # Public & protected medicine catalog endpoints
│       └── orders.py        # Protected order processing endpoints
├── .dockerignore
├── .env                     # Local environment variables
├── .gitignore
├── Dockerfile               # Production container definition
├── docker-compose.yml       # Multi-container orchestration (API + Mongo)
├── requirements.txt         # Project dependencies
└── README.md
```

---

## 🚦 API Endpoints

### 🔐 Authentication (`/auth`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Register a new user account | ❌ No |
| `POST` | `/auth/login` | Authenticate and obtain JWT access token | ❌ No |

### 💊 Medicine Inventory (`/medicines`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/medicines/` | List all medicines in the catalog | ❌ No |
| `GET` | `/medicines/search?name={query}` | Case-insensitive partial name search | ❌ No |
| `GET` | `/medicines/{id}` | Retrieve medicine details by ID | ❌ No |
| `POST` | `/medicines/` | Add a new medicine to inventory | 🔒 Yes (Bearer JWT) |
| `PUT` | `/medicines/{id}` | Update medicine details / stock | 🔒 Yes (Bearer JWT) |
| `DELETE` | `/medicines/{id}` | Delete a medicine by ID | 🔒 Yes (Bearer JWT) |

### 🛒 Orders (`/orders`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/orders/` | Place a new order with atomic stock decrement | 🔒 Yes (Bearer JWT) |
| `GET` | `/orders/{id}` | Retrieve order details by ID | ❌ No |

---

## 💻 Getting Started (Local Setup)

### 1. Clone the repository
```bash
git clone https://github.com/Prerna3e/medicine-inventory-api.git
cd medicine-inventory-api
```

### 2. Create and activate virtual environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=medicine_inventory
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 5. Run the Application
Ensure MongoDB is running locally, then start the development server:
```bash
uvicorn app.main:app --reload
```
The API will be available at: **`http://127.0.0.1:8000`**
Interactive Swagger Documentation: **`http://127.0.0.1:8000/docs`**

---

## 🐳 Docker Setup

To spin up both the FastAPI application and MongoDB using Docker Compose:

```bash
docker-compose up --build -d
```

- **API URL**: `http://localhost:8000`
- **Swagger Docs**: `http://localhost:8000/docs`
- **MongoDB Port**: `27017`

To stop the containers:
```bash
docker-compose down
```

---

## 🧪 Testing & Verification Workflow

### 1. Register and Login
- **Register**: `POST /auth/register`
  ```json
  {
    "username": "dr_smith",
    "password": "securepassword123"
  }
  ```
- **Login**: `POST /auth/login`
  ```json
  {
    "username": "dr_smith",
    "password": "securepassword123"
  }
  ```
  Returns `{"access_token": "...", "token_type": "bearer"}`.

### 2. Authorize in Swagger UI
Click the **Authorize** button at `http://127.0.0.1:8000/docs` and enter your Bearer token.

### 3. Create Medicines
- `POST /medicines/`
  ```json
  {
    "name": "Paracetamol 500mg",
    "price": 5.50,
    "category": "Analgesics",
    "stock": 100,
    "manufacturer": "GSK"
  }
  ```

### 4. Search Medicines
- `GET /medicines/search?name=para`
  Returns all medicines matching `"para"` (case-insensitive).

### 5. Create Order with Concurrency-Safe Stock Validation
- `POST /orders/`
  ```json
  {
    "medicines": [
      {
        "medicine_id": "<MEDICINE_ID>",
        "quantity": 5
      }
    ]
  }
  ```
  - Computes `total_price` server-side (`5 * 5.50 = 27.50`).
  - Atomically decrements medicine stock (`100 -> 95`).
  - Returns `409 Conflict` if requested quantity exceeds current inventory.

---

## 📄 License
MIT License. Created as a backend portfolio project targeting healthcare-technology roles.
