import logging
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.routes import init_database, router
from app.config import get_settings
from app.utils.logging import setup_logging


settings = get_settings()
setup_logging()
logger = logging.getLogger("novel_ai_writer")

app = FastAPI(
    title=settings.app_name,
    description="面向网络小说作者的 AI 创作、章节生成、素材检索、投稿整理与数据统计系统。",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.middleware("http")
async def request_log_middleware(request: Request, call_next):
    started = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = int((time.perf_counter() - started) * 1000)
        status_code = response.status_code if response else 500
        logger.info("%s %s status=%s duration_ms=%s", request.method, request.url.path, status_code, duration_ms)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning("HTTPException path=%s status=%s detail=%s", request.url.path, exc.status_code, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail, "detail": exc.detail, "path": request.url.path},
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("ValidationError path=%s errors=%s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": "请求参数校验失败", "detail": exc.errors(), "path": request.url.path},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("UnhandledException path=%s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "detail": "服务器内部错误", "path": request.url.path},
    )


@app.on_event("startup")
def on_startup():
    init_database()
