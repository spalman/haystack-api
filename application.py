import logging

import uvicorn
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from fastapi import Response
from controller.errors.http_error import http_error_handler
from controller.router import router as api_router

logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
logger = logging.getLogger(__name__)
logging.getLogger("elasticsearch").setLevel(logging.WARNING)


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


logger.info("Open http://127.0.0.1:8000/docs to see Swagger API Documentation.")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)