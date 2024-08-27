from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import time

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

def register_middleware(app: FastAPI):
    pass
    @app.middleware("http")
    async def custom_logger(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        message = f"{request.client.host}:{request.client.port}  {request.method} - {request.url.path} - status_code:{response.status_code} - completed:{process_time}s"
        print(message)
        return response
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
