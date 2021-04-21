import logging
import os
from typing import Optional
import shutil
from fastapi import APIRouter
from fastapi import HTTPException

# from config import (
#     FILE_UPLOAD_PATH,
# )


import gdown

logger = logging.getLogger(__name__)
router = APIRouter()
FILE_UPLOAD_PATH = "datasets"
os.makedirs(FILE_UPLOAD_PATH, exist_ok=True)  # create directory for uploading files
G_DRIVE_TEMPLATE = "https://drive.google.com/uc?id={}"


@router.post("/file-upload")
def upload_file_to_document_store(
    dataset_name: str,
    retriever_pt_file_id: Optional[str]=None,
    sql_db_file_id: Optional[str]=None,
    index_file_file_id: Optional[str]=None,
):
    os.makedirs(
        os.path.join(FILE_UPLOAD_PATH, dataset_name), exist_ok=True
    )  # create directory for uploading files
    path_ = os.path.join(FILE_UPLOAD_PATH, dataset_name)
    if retriever_pt_file_id:
        if not os.path.exists(os.path.join(path_, "retriever.pt")):
            gdown.download(
                G_DRIVE_TEMPLATE.format(retriever_pt_file_id),
                os.path.join(path_, "retriever.pt.zip"),
                quiet=True,
            )
            shutil.unpack_archive(os.path.join(path_, "retriever.pt.zip"), path_)
    
        if not os.path.exists(os.path.join(path_, "retriever.pt")):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to download retriever.pt. Please try again",
            )
    if sql_db_file_id:
        if not os.path.exists(os.path.join(path_, "haystack_faiss.db")):
            gdown.download(
                G_DRIVE_TEMPLATE.format(sql_db_file_id),
                os.path.join(path_, "haystack_faiss.db"),
                quiet=True,
            )
        if not os.path.exists(os.path.join(path_, "haystack_faiss.db")):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to download haystack_faiss.db. Please try again",
            )
    if index_file_file_id:
        if not os.path.exists(os.path.join(path_, "faiss.index")):
            gdown.download(
                G_DRIVE_TEMPLATE.format(index_file_file_id),
                os.path.join(path_, "faiss.index"),
                quiet=True,
            )
        if not os.path.exists(os.path.join(path_, "haystack_faiss.db")):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to download faiss.index. Please try again",
            )
    return "Files upload was successful."


# if __name__ == "__main__":
#     path__ = os.path.join(FILE_UPLOAD_PATH, "melanin", "retriever.pt.zip")
#     shutil.unpack_archive(path__, os.path.join(FILE_UPLOAD_PATH, "melanin"))
