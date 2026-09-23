import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.routes.patients import router as patient_router

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("patient_api")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Open CORS so the Next.js dashboard (browser) and Vapi's server-side tool
# calls can both reach the API. Acceptable for this assessment; a
# production system would restrict this to known origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patient_router)


@app.get("/health")
async def health_check():
    return {"data": {"status": "ok", "service": settings.APP_NAME}, "error": None}


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    details = exc.errors()
    first_error = details[0] if details else {}
    location = ".".join(str(item) for item in first_error.get("loc", []))
    message = first_error.get("msg", "Validation error.")
    if location:
        message = f"Validation error in {location}: {message}"

    return JSONResponse(
        status_code=422,
        content={"data": None, "error": {"message": message}},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # exc.detail can be a plain string, or a dict — the duplicate-patient
    # check in routes/patients.py raises a dict detail so it can also
    # return the existing record alongside the message.
    error_body = exc.detail if isinstance(exc.detail, dict) else {"message": exc.detail}
    return JSONResponse(
        status_code=exc.status_code,
        content={"data": None, "error": error_body},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(
        status_code=500,
        content={"data": None, "error": {"message": "Internal server error."}},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
