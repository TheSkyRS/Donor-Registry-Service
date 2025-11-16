# 🩸 Donor Registry Service

**FastAPI + Pydantic v2 + SQLAlchemy + MySQL**  

Sprint 1 delivered full API stubs (HTTP 501, OpenAPI ready).  
**Sprint 2 now provides complete database-backed CRUD, filtering, pagination, linked data (HATEOAS), and ETag support.**

---

## 🚀 Run

```bash
# local
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python main.py
open http://localhost:8000/docs

# docker related
docker build --platform linux/amd64 -t yonghaolin/donor-registry-service:latest .
docker push yonghaolin/donor-registry-service:latest

# cloud run
gcloud run deploy donor-registry-service \
  --image docker.io/yonghaolin/donor-registry-service:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --add-cloudsql-instances cloud-computing-478420:us-central1:donor-db \
  --set-env-vars DATABASE_URL="mysql+pymysql://root:yl5763@/donor_registry?unix_socket=/cloudsql/cloud-computing-478420:us-central1:donor-db"
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

MS1 acts as the **authoritative donor database** for the entire system.

---

## 📂 Folder Layout (Sprint 2)

```text
.
├─ main.py                     
├─ requirements.txt            
├─ framework/
│  └─ app_factory.py           # App factory for FastAPI
├─ db/
│  ├─ session.py               # SQLAlchemy Engine + SessionLocal
│  └─ models.py                # ORM: donors / organs / consents
├─ models/                     # Pydantic schemas
│  ├─ enums.py
│  ├─ health.py
│  ├─ donor.py
│  ├─ organ.py
│  └─ consent.py
├─ resources/                  # HTTP routes (FastAPI)
│  ├─ donors.py
│  ├─ organs.py
│  ├─ consents.py
│  ├─ health.py
│  ├─ root.py
│  └─ __init__.py
├─ services/                   # Business logic + DB interaction
│  ├─ donors_service.py
│  ├─ organs_service.py
│  └─ consents_service.py
├─ utils/
│  ├─ ip.py
│  ├─ time.py
│  └─ responses.py
└─ requests/
   └─ smoke.http               # VS Code REST Client smoke tests
```

---

## 🧱 Layering at a glance

| Layer        | Responsibility                                   |
|-------------|---------------------------------------------------|
| **models/** | Pydantic schemas (validation + OpenAPI docs)      |
| **resources/** | REST endpoints (async FastAPI `APIRouter`)     |
| **services/** | Business logic, SQLAlchemy queries, domain validation |
| **db/**     | SQLAlchemy ORM models + engine configuration      |
| **utils/**  | IP/time helpers, common utilities   |

### Sprint 2 Enhancements

- ✅ SQLAlchemy persistence (MySQL)
- ✅ Actual CRUD for donors, organs, consents
- ✅ Async FastAPI endpoints
- ✅ Clean domain error → HTTP translation
- ✅ Linked data / HATEOAS-style `_links`
- ✅ Pagination for all top-level resources
- ✅ Correct `201 Created` + `Location` headers
- ✅ ETag + `If-Match` version control for donors

---

## 🌐 API Surface (Sprint 2 — fully implemented)

### Donors

| Method | Path            | Description                                                |
|--------|-----------------|------------------------------------------------------------|
| GET    | `/donors`       | List donors (filter by `name`, `blood_type`, `status`; pagination) |
| POST   | `/donors`       | Create donor (`201 Created` + `Location` header)          |
| GET    | `/donors/{id}`  | Retrieve donor by ID (includes `ETag`)                    |
| PUT    | `/donors/{id}`  | Update donor (**requires** `If-Match` ETag)               |
| DELETE | `/donors/{id}`  | Delete donor                                              |

### Organs

| Method | Path                         | Description                                       |
|--------|------------------------------|---------------------------------------------------|
| GET    | `/organs`                    | Filter by `donor_id` / `organ_type`, pagination   |
| GET    | `/organs/{id}`               | Retrieve organ by ID                              |
| PUT    | `/organs/{id}`               | Update organ                                      |
| DELETE | `/organs/{id}`               | Delete organ                                      |
| GET    | `/donors/{donor_id}/organs`  | List organs belonging to a donor                  |
| POST   | `/donors/{donor_id}/organs`  | Create organ for donor                            |

### Consents

| Method | Path                           | Description                                       |
|--------|--------------------------------|---------------------------------------------------|
| GET    | `/consents`                    | Filter by `donor_id` / `status`, pagination       |
| GET    | `/consents/{id}`               | Retrieve consent by ID                            |
| PUT    | `/consents/{id}`               | Update consent                                    |
| DELETE | `/consents/{id}`               | Delete consent                                    |
| GET    | `/donors/{donor_id}/consents`  | List consents for donor                           |
| POST   | `/donors/{donor_id}/consents`  | Create consent for donor                          |

---

## ✨ Sprint 2 Feature Highlights

### 🔗 Linked Data (HATEOAS)

Each donor response includes:

```json
"_links": {
  "self": "/donors/123",
  "organs": "/organs?donor_id=123",
  "consents": "/consents?donor_id=123"
}
```

### 📄 Pagination

Supported on `/donors`, `/organs`, `/consents`:

```text
?limit=50&offset=0
```

Example response:

```json
{
  "items": [ /* ... */ ],
  "count": 50,
  "total": 243,
  "_links": {
    "self": "/donors?limit=50&offset=0",
    "next": "/donors?limit=50&offset=50",
    "prev": null
  }
}
```

### 🔍 Filtering Examples

```bash
/donors?name=bob&status=active
/organs?donor_id=<uuid>&organ_type=kidney
/consents?donor_id=<uuid>&status=granted
```

### 🏷 ETag Version Control

Optimistic concurrency for donors:

```http
GET /donors/{id}
ETag: W/"<sha256>"

PUT /donors/{id}
If-Match: W/"<sha256>"
```

If mismatched:

```http
412 Precondition Failed
```

---

## 🗄 Database Model (MySQL via SQLAlchemy)

### donors

| Column      | Type          |
|-------------|---------------|
| id          | UUID          |
| first_name  | varchar(100)  |
| last_name   | varchar(100)  |
| dob         | date          |
| blood_type  | enum          |
| status      | enum          |
| created_at  | datetime      |
| updated_at  | datetime      |

### organs

| Column        | Type          |
|---------------|---------------|
| id            | UUID          |
| donor_id      | FK(donors.id) |
| organ_type    | enum          |
| condition     | varchar(100)  |
| retrieved_at  | datetime      |
| created_at    | datetime      |
| updated_at    | datetime      |

### consents

| Column        | Type           |
|---------------|----------------|
| id            | UUID           |
| donor_id      | FK(donors.id)  |
| scope         | varchar(200)   |
| status        | enum           |
| signed_at     | datetime       |
| revoked_at    | datetime       |
| created_at    | datetime       |
| updated_at    | datetime       |

---

## 🧪 Development Tips

Hot reload:

```bash
uvicorn main:app --reload
```

Smoke tests:

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/donors
```

---

## 🗺 Roadmap (Sprint 3)

- TODO
