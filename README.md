# XML Library Management System

A complete XML-based library management system demonstrating XML creation, XSD validation, XPath queries, XSLT transformation, DOM/streaming parsing, REST API with XML content negotiation, and external service integration.

**Course:** 155-8056 XML and Web Services  
**Stack:** Python (FastAPI, lxml, httpx) + Next.js (React, Tailwind CSS)

---

## Project Structure

```
XMLYENİ/
├── backend/
│   ├── data/
│   │   ├── library.xml          # 27 books, 8 members, 10 borrowings
│   │   ├── invalid_library.xml  # Intentionally invalid for XSD demo
│   │   ├── schema.xsd           # Advanced XSD constraints
│   │   └── report.xslt          # HTML dashboard transformation
│   ├── src/
│   │   ├── main.py              # FastAPI application
│   │   ├── xml_manager.py       # DOM + iterparse CRUD
│   │   ├── validators.py        # XSD validation
│   │   ├── xpath_queries.py     # 6 complex XPath queries
│   │   ├── xslt_transformer.py  # XSLT HTML reports
│   │   ├── external_service.py  # Open Library integration
│   │   └── routers/             # API v1 routes
│   └── tests/                   # pytest suite
├── frontend/                    # Next.js web application
├── postman/                     # Postman collection
└── README.md
```

---

## Features

| Feature | Implementation |
|---------|----------------|
| XML Data | 27 nested book records + members + borrowings |
| XSD Validation | ISBN pattern, genre enum, email pattern, IDREF |
| XPath | 6 queries with predicates, count(), contains() |
| XSLT | HTML dashboard report |
| DOM Parsing | lxml.etree full tree read/write |
| Streaming | lxml.etree.iterparse (SAX-like) |
| REST API | GET/POST/PUT/DELETE with XML only |
| API Versioning | `/api/v1/` prefix |
| Authentication | API Key on POST/PUT/DELETE |
| Filtering | Genre + search via XPath query params |
| Pagination | `?page=` and `?limit=` |
| External API | Open Library JSON → XML conversion |
| Frontend | Client-side DOMParser, XML serialization |

---

## Backend Setup

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Server

```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

- **Swagger UI:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health
- **XSLT Dashboard:** http://localhost:8000/api/v1/reports/dashboard
- **Validation demo:** http://localhost:8000/api/v1/validation/demo

### Run Tests

```bash
cd backend
source venv/bin/activate
pytest -v
```

### Validate XML Manually

```bash
cd backend
source venv/bin/activate
python -c "from src.validators import validate_file_pair; from src.config import LIBRARY_XML, INVALID_LIBRARY_XML; print(validate_file_pair(LIBRARY_XML, INVALID_LIBRARY_XML))"
```

### Run XPath Demo

```bash
cd backend
source venv/bin/activate
python -c "from src.xpath_queries import run_all_queries; import json; print(json.dumps(run_all_queries(), indent=2))"
```

---

## Frontend Setup

### Prerequisites
- Node.js 18+
- npm

### Installation

```bash
cd frontend
npm install
cp .env.local.example .env.local
```

### Run Development Server

```bash
cd frontend
npm run dev
```

Open http://localhost:3000

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |
| `NEXT_PUBLIC_API_KEY` | `library-api-key-dev-2026` | API key for write operations |

---

## API Reference

All endpoints under `/api/v1/` return `application/xml` unless noted.

**Headers:**
- `Accept: application/xml` (required for XML endpoints)
- `Content-Type: application/xml` (for POST/PUT)
- `X-API-Key: library-api-key-dev-2026` (for POST/PUT/DELETE)

### Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/books` | No | List books (`?genre=`, `?search=`, `?page=`, `?limit=`) |
| GET | `/api/v1/books/{id}` | No | Get single book |
| POST | `/api/v1/books` | API Key | Create book (XML body) |
| PUT | `/api/v1/books/{id}` | API Key | Update book (XML body) |
| DELETE | `/api/v1/books/{id}` | API Key | Delete book |
| GET | `/api/v1/members` | No | List members (`?membershipType=`, `?search=`) |
| GET | `/api/v1/members/{id}` | No | Get single member |
| POST | `/api/v1/members` | API Key | Register member (XML body) |
| PUT | `/api/v1/members/{id}` | API Key | Update member |
| DELETE | `/api/v1/members/{id}` | API Key | Delete member (no active loans) |
| GET | `/api/v1/borrowings` | No | List borrowings (`?status=`, `?memberRef=`, `?bookRef=`) |
| GET | `/api/v1/borrowings/{id}` | No | Get single borrowing |
| POST | `/api/v1/borrowings` | API Key | Check out book (circulation) |
| PUT | `/api/v1/borrowings/{id}/return` | API Key | Return book |
| PUT | `/api/v1/borrowings/{id}` | API Key | Update borrowing record |
| DELETE | `/api/v1/borrowings/{id}` | API Key | Delete returned record only |
| GET | `/api/v1/reports/dashboard` | No | XSLT HTML report |
| GET | `/api/v1/reports/xpath` | No | XPath query results as XML |
| GET | `/api/v1/external/enrich/{isbn}` | No | Open Library enrichment |

## Circulation Business Rules

| Rule | Behavior |
|------|----------|
| Loan limits | student: 5, faculty: 10, public: 3 concurrent loans |
| Loan periods | student: 14 days, faculty: 30 days, public: 21 days |
| Checkout | Decrements `availableCopies`, auto-sets dates |
| Return | Increments `availableCopies`, sets status to `returned` |
| Overdue | Active loans past `dueDate` marked `overdue` on read |
| Delete member | Blocked if active/overdue loans exist |
| Delete book | Blocked if active/overdue loans exist |
| Delete borrowing | Only allowed for `returned` records |

---

```xml
<?xml version="1.0" encoding="UTF-8"?>
<error>
  <code>404</code>
  <message>Book not found</message>
  <detail>id=bk-999</detail>
</error>
```

---

## cURL Examples

### List all Sci-Fi books

```bash
curl -H "Accept: application/xml" \
  "http://localhost:8000/api/v1/books?genre=Sci-Fi&page=1&limit=5"
```

### Get book by ID

```bash
curl -H "Accept: application/xml" \
  "http://localhost:8000/api/v1/books/bk-001"
```

### Create a new book

```bash
curl -X POST \
  -H "Accept: application/xml" \
  -H "Content-Type: application/xml" \
  -H "X-API-Key: library-api-key-dev-2026" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<book isbn="978-0-99-777666-5">
  <title>XML Processing Guide</title>
  <author>Jane Developer</author>
  <publisher>Tech Press</publisher>
  <categories><category>Technology</category></categories>
  <publicationYear>2024</publicationYear>
  <availableCopies>3</availableCopies>
</book>' \
  "http://localhost:8000/api/v1/books"
```

### Update a book

```bash
curl -X PUT \
  -H "Accept: application/xml" \
  -H "Content-Type: application/xml" \
  -H "X-API-Key: library-api-key-dev-2026" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<book isbn="978-0-13-468599-1">
  <title>Effective Java (3rd Edition)</title>
  <author>Joshua Bloch</author>
  <publisher>Addison-Wesley</publisher>
  <categories><category>Technology</category></categories>
  <publicationYear>2018</publicationYear>
  <availableCopies>10</availableCopies>
</book>' \
  "http://localhost:8000/api/v1/books/bk-001"
```

### Delete a book

```bash
curl -X DELETE \
  -H "Accept: application/xml" \
  -H "X-API-Key: library-api-key-dev-2026" \
  "http://localhost:8000/api/v1/books/bk-028"
```

### Enrich ISBN from Open Library

```bash
curl -H "Accept: application/xml" \
  "http://localhost:8000/api/v1/external/enrich/9780134685991"
```

### Trigger error (missing API key)

```bash
curl -X POST \
  -H "Accept: application/xml" \
  -H "Content-Type: application/xml" \
  -d '<book isbn="978-0-99-111222-3"><title>Test</title></book>' \
  "http://localhost:8000/api/v1/books"
```

---

## Evidence Checklist (Report & Video)

Use this checklist when preparing your project report and video:

- [ ] Show `library.xml` nested structure (books, members, borrowings)
- [ ] Demonstrate XSD validation success on `library.xml`
- [ ] Demonstrate XSD validation failure on `invalid_library.xml` with error log
- [ ] Run and show results of 5+ XPath queries
- [ ] Show XSLT HTML dashboard output
- [ ] Demo REST API with XML request/response (Postman or curl)
- [ ] Demo POST create book with XML payload
- [ ] Demo PUT update and DELETE with API key
- [ ] Demo Open Library enrichment endpoint
- [ ] Demo at least one error case (404, 400, 401)
- [ ] Show frontend parsing XML with DOMParser
- [ ] Show frontend serializing form to XML before POST
- [ ] Explain DOM vs iterparse streaming in code

---

## License

Academic project for Mersin University — XML and Web Services course.
