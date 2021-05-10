import logging
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from controller.errors.http_error import http_error_handler
from controller.router import router as api_router

import logging
from fastapi.logger import logger as fastapi_logger


def get_application() -> FastAPI:
    application = FastAPI(title="Haystack-API", debug=True, version="0.1")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_exception_handler(HTTPException, http_error_handler)

    application.include_router(api_router)

    return application


app = get_application()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
