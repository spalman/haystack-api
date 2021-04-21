from fastapi import APIRouter

from controller import file_upload
from controller import search

router = APIRouter()

router.include_router(search.router, tags=["search"])
router.include_router(file_upload.router, tags=["file-upload"])
