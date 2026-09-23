# Voice AI Patient Registration — Backend

FastAPI REST API + Supabase PostgreSQL backend for the Voice AI Patient
Registration take-home assessment. This is Layer 3 of the system
(Phone/Vapi → LLM → **this API** → Supabase → Next.js dashboard).

## Architecture

```
app/
├── main.py              # FastAPI app, CORS, global exception handlers, /health
├── config.py             # Loads env vars (.env) into a Settings object
├── database.py           # Lazy Supabase client singleton
├── schemas/
│   └── patient.py        # Pydantic models: validation rules live here ONLY
├── routes/
│   └── patients.py       # HTTP layer: request/response, status codes
└── services/
    └── patient_service.py # Supabase queries, isolated from HTTP concerns
tests/
└── test_patient_schema.py # Validation unit tests (no DB required)
```

**Separation of concerns:** routes only handle HTTP status codes and
request/response shaping; all Supabase queries live in `patient_service.py`;
all validation rules live in `schemas/patient.py`. This makes each layer
independently testable and easy to explain in an interview.

## Tech stack justification

- **FastAPI** — async, automatic OpenAPI/Swagger docs at `/docs`, native
  Pydantic integration for request validation (a core requirement).
- **Supabase (PostgreSQL)** — managed Postgres with a REST-friendly Python
  client (`supabase-py`), so no separate ORM/migration setup was needed
  within the 3-hour window, while keeping a real relational schema.
- **Railway / Render** — both auto-deploy from GitHub via the included
  `Procfile`, and give a public HTTPS URL, which Vapi's tool-calling
  requires (it cannot call `localhost`).

## Setup instructions

1. `cd backend`
2. Activate your virtual environment.
3. `pip install -r requirements.txt`
4. `cp .env.example .env` and fill in `SUPABASE_URL` and `SUPABASE_KEY`
   (Supabase dashboard → Project Settings → API).
5. Run the server:
   ```
   uvicorn app.main:app --reload
   ```
6. Open `http://127.0.0.1:8000/docs` for interactive Swagger UI.

## Environment variables

| Variable      | Required | Description                                  |
|---------------|----------|-----------------------------------------------|
| SUPABASE_URL  | Yes      | Your Supabase project URL                     |
| SUPABASE_KEY  | Yes      | Supabase service_role or anon key             |
| DEBUG         | No       | `true` for verbose logging (default: false)   |

## API endpoints

All responses use the envelope `{"data": ..., "error": ...}`.

| Method | Endpoint            | Notes                                              |
|--------|----------------------|-----------------------------------------------------|
| GET    | `/health`             | Liveness check                                      |
| GET    | `/patients`           | List; optional `?last_name=&date_of_birth=&phone_number=` filters |
| GET    | `/patients/{id}`      | 404 if not found or soft-deleted                    |
| POST   | `/patients`           | 201 on success; **409** if phone_number already exists (see Bonus) |
| PUT    | `/patients/{id}`      | Partial update; 400 if body is empty                |
| DELETE | `/patients/{id}`      | Soft delete — sets `deleted_at`, never removes the row |

## Bonus features implemented

- **Duplicate-caller detection by phone number**: `POST /patients` checks
  for an existing non-deleted patient with the same `phone_number` first.
  If found, it returns `409 Conflict` with the existing record in
  `error.existing_patient`, so the voice agent (or dashboard) can ask
  "We already have a record for X — update instead?" rather than creating
  duplicates.
- **Automated tests**: `tests/test_patient_schema.py` covers the validation
  rules (future DOB, non-numeric phone, invalid state/sex/zip) without
  needing a live database. Run with `pytest`.
- **Observability**: `patient_service.py` logs created/updated/deleted
  patient IDs and names to stdout, satisfying the logging requirement.

## Known limitations / trade-offs

- CORS is fully open (`allow_origins=["*"]`) for simplicity within the time
  limit; a production system would restrict this to the dashboard's and
  Vapi's actual origins.
- Duplicate-phone detection is application-level (a race condition between
  two simultaneous calls with the same number is theoretically possible);
  a DB-level unique constraint would close this gap but wasn't added since
  the schema was already created and out-of-scope to change without
  confirmation.
- `pydantic`'s v1-style `@validator` is used (works under Pydantic v2 with
  a deprecation warning) rather than `@field_validator`, to keep the code
  closer to what was already scaffolded.
- No authentication on the API — acceptable per the assessment's explicit
  scope (no HIPAA / production security expected).
- `first_name`/`last_name` validation follows the spec literally (letters,
  hyphens, apostrophes only) — a compound name with a space (e.g. "Van Dyke")
  would be rejected. Not widened beyond the spec's wording.
- `state` is validated against the 50 U.S. states + DC only; U.S.
  territories (PR, GU, VI, etc.) are not in the allowed list.
- `date_of_birth` is accepted/returned in ISO 8601 (`YYYY-MM-DD`) rather
  than literal `MM/DD/YYYY`, since JSON REST APIs conventionally use ISO
  dates and Pydantic's `date` type parses/validates that format natively;
  `MM/DD/YYYY` is treated as the spoken/display format for the voice agent
  layer, not the API wire format.
- `updated_at` is set explicitly by the application on every `PUT` (the
  Supabase column only auto-fills via `DEFAULT NOW()` on insert, and no
  DB trigger exists for updates — adding one would be a schema change).

## Next steps (not yet done)

1. Deploy this backend to Railway or Render to get a public HTTPS URL.
2. Configure the Vapi assistant (system prompt + a `create_patient` /
   `find_patient_by_phone` tool pointing at the deployed URL).
3. Provision a Vapi phone number and link it to the assistant.
4. Build the Next.js dashboard to list patients from `GET /patients`.
5. End-to-end test: call the number twice and confirm data persists.
