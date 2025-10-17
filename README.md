# 🩸 Donor Registry Service

**FastAPI + Pydantic v2**  
Sprint 1 stubs (HTTP 501), OpenAPI ready.

---

## 🚀 Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
open http://localhost:8000/docs
```

---

## 📘 Overview

This repository implements **Microservice 1: Donor Registry**, one of three services in the team cloud computing project:

| Service | Description |
|----------|--------------|
| [**MS1 – Donor Registry (this repo)**](https://github.com/TheSkyRS/Donor-Registry-Service) | Donor/Organ/Consent |
| [**MS2 – Recipient Waitlist**](https://github.com/zl3508/recipient-waitlist-service) | Recipient/Hospital/Need |
| [**MS3 – Organ Matching & Notification**](https://github.com/AyalYakobe/matchmaking_and_notifications_serivce) | API‑first with Swagger |

### Typical Flow

1. A **Donor** is registered in the system.  
2. The Donor’s available **Organs** are recorded.  
3. The Donor’s **Consent** for donation is captured.  
4. The **Organ Matching Service (MS3)** uses this data to perform **organ matching** with recipient needs from **MS2**.

---

## 📂 Folder Layout

```
.
├─ main.py                     # App entrypoint: create FastAPI
├─ requirements.txt            
├─ framework/
│  └─ app_factory.py           # App factory for consistent FastAPI creation
├─ middleware/
├─ models/
│  ├─ __init__.py
│  ├─ enums.py                 # Shared enums (blood type, organ type, consent status)
│  ├─ health.py                # Model for /health responses
│  ├─ donor.py                 # Donor* (Base/Create/Read/Update)
│  ├─ organ.py                 # Organ* (Base/Create/Read/Update)
│  └─ consent.py               # Consent* (Base/Create/Read/Update)
├─ resources/
│  ├─ __init__.py              # Merges per-resource APIRouters into single `api`
│  ├─ root.py                  # GET /
│  ├─ health.py                # GET /health, GET /health/{path_echo}
│  ├─ donors.py                # /donors… endpoints (Sprint 1 → 501)
│  ├─ organs.py                # /organs… endpoints (Sprint 1 → 501)
│  └─ consents.py              # /consents… endpoints (Sprint 1 → 501)
├─ services/
│  ├─ __init__.py              # Business logic (CRUD/DB) → Sprint 2
├─ utils/
│  ├─ __init__.py
│  ├─ ip.py                    # Helper to get host IP (used by /health)
│  ├─ time.py                  # UTC ISO-8601 timestamp helper
│  └─ responses.py             # `not_implemented()` → unified HTTP 501 stub
└─ requests/
   └─ smoke.http               # VS Code REST Client smoke tests
```

---

## 🧱 Layering at a glance

| Layer | Responsibility |
|--------|----------------|
| **models/** | Define input/output schemas for validation + docs |
| **resources/** | Expose HTTP endpoints (thin controllers using APIRouter) |
| **services/** | Implement business logic and data persistence |
| **main.py** | Creates app |

---

## 🌐 API Surface (Sprint 1 stubs)

All endpoints are defined and documented; they currently respond with HTTP `501 Not Implemented` via `utils.responses.not_implemented()`.

### Root & Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Welcome message, link to `/docs` |
| `GET` | `/health` | Health check (status, timestamp, IP, optional echo) |
| `GET` | `/health/{path_echo}` | Health check with path echo |

---

### Donors

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/donors` | List donors (optionally filter by status or blood type) |
| `POST` | `/donors` | Create new donor (`201`) |
| `GET` | `/donors/{id}` | Retrieve donor by ID |
| `PUT` | `/donors/{id}` | Update donor record |
| `DELETE` | `/donors/{id}` | Delete donor (`204`) |

---

### Organs (subresource + standalone)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/organs` | List all organs (optionally filter by donor or organ type) |
| `GET` | `/organs/{id}` | Retrieve an organ by ID |
| `PUT` | `/organs/{id}` | Update organ |
| `DELETE` | `/organs/{id}` | Delete organ (`204`) |
| `GET` | `/donors/{donor_id}/organs` | List organs belonging to a donor |
| `POST` | `/donors/{donor_id}/organs` | Add organ record for a donor (`201`) |

---

### Consents (subresource + standalone)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/consents` | List all consents (optionally filter by donor or status) |
| `GET` | `/consents/{id}` | Retrieve consent by ID |
| `PUT` | `/consents/{id}` | Update consent |
| `DELETE` | `/consents/{id}` | Delete consent (`204`) |
| `GET` | `/donors/{donor_id}/consents` | List consents for donor |
| `POST` | `/donors/{donor_id}/consents` | Create consent for donor (`201`) |
---

## 🧩 Data Models (Pydantic v2)

### Enums (`models/enums.py`)

| Enum | Values |
|------|---------|
| **BloodType** | `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-` |
| **OrganType** | `heart`, `liver`, `kidney`, `lung`, `pancreas`, `intestine` |
| **ConsentStatus** | `granted`, `revoked`, `pending` |
| **CommonStatus** | `active`, `inactive` |

---

### Donor (`models/donor.py`)

- **DonorBase**
  - `full_name: str (1–200)` 
  - `dob: date`
  - `blood_type: BloodType`
  - `status: CommonStatus = active`
- **DonorCreate** = DonorBase  
- **DonorRead** = DonorBase + `id: UUID`, `created_at`, `updated_at`
- **DonorUpdate** — all fields optional

---

### Organ (`models/organ.py`)

- **OrganBase**
  - `organ_type: OrganType`
  - `condition: str (1–100)`
  - `retrieved_at?: datetime`
- **OrganCreate** = OrganBase  
- **OrganRead** = OrganBase + `id: UUID`, `donor_id: UUID`, `created_at`, `updated_at`
- **OrganUpdate** — all fields optional

---

### Consent (`models/consent.py`)

- **ConsentBase**
  - `scope: str` (e.g. "all organs" or "specific organs")
  - `status: ConsentStatus = pending`
  - `signed_at?: datetime`
  - `revoked_at?: datetime`
- **ConsentCreate** = ConsentBase  
- **ConsentRead** = ConsentBase + `id: UUID`, `donor_id: UUID`, `created_at`, `updated_at`
- **ConsentUpdate** — all fields optional

---

### Health (`models/health.py`)

- `status: int`
- `status_message: str`
- `timestamp: str (UTC ISO-8601)`
- `ip_address: str`
- `echo?: str`
- `path_echo?: str`

---

## 🧪 Development Tips

Run with hot-reload:

```bash
uvicorn main:app --reload
```

Smoke tests:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/donors     # 501 (expected in Sprint 1)
```

Replace `not_implemented()` with real logic in `services/` for Sprint 2  
(start with in-memory dicts, then integrate MySQL).

---

## 🗺️ Roadmap (Sprint 2+)

- Implement in-memory CRUD in `services/` and connect to endpoints.  
- Add `/health/ready` readiness check (lightweight DB ping).  
- Introduce MySQL persistence (schema aligned with enums).  
- Load connection settings from `.env`.  
- Optionally add CORS, request logging, and typed settings.
