from fastapi import FastAPI, Request
from app.api.routes import router
from app.db.database import init_db
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import nltk


@asynccontextmanager
async def lifespan(app: FastAPI):
    nltk.download("punkt")
    nltk.download("punkt_tab")
    nltk.download("stopwords")
    nltk.download("wordnet")
    nltk.download("averaged_perceptron_tagger_eng")

    init_db()

    yield


app = FastAPI(
    title="Faketify API",
    description="FastAPI backend for political hoax detection",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Failed",
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
        },
    )


# Include routes
app.include_router(router)
