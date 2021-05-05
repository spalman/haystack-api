import json
import logging
import time
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from fastapi import HTTPException

from config import (
    LOG_LEVEL,
)

from controller.request import Question
from controller.response import Answers, AnswersToIndividualQuestion

from controller.utils import RequestLimiter
from haystack.document_store.faiss import FAISSDocumentStore
from haystack.reader.farm import FARMReader

from haystack.retriever.dense import DensePassageRetriever
from haystack.pipeline import DocumentSearchPipeline, ExtractiveQAPipeline

logger = logging.getLogger("haystack")
logger.setLevel(LOG_LEVEL)

router = APIRouter()
DATASETS_DIR = "datasets"
CURRENT_DATASET = None
PIPELINES = {"QA": None, "SemanticSearch": None}
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=False)


def check_datasets():
    """Checks if dataset contains all files"""
    datasets = []
    dirs = os.listdir(DATASETS_DIR)
    model_files = ["retriever.pt", "haystack_faiss.db", "faiss.index"]
    for dir in dirs:
        files = os.listdir(os.path.join(DATASETS_DIR, dir))
        if all(f in files for f in model_files):
            datasets.append(dir)
    return datasets


# Init global components: DocumentStore, Retriever, Reader, Finder
def load_model(dataset_name):
    global CURRENT_DATASET
    global PIPELINES
    datasets = check_datasets()
    if not dataset_name in datasets:
        raise HTTPException(
            status_code=500,
            detail=f"Dataset not loaded. Load data first. Available datasets: {list(datasets)}",
        )
    faiss_index = os.path.join(DATASETS_DIR, dataset_name, "faiss.index")
    sql_url = f"sqlite:///{os.path.join(DATASETS_DIR,dataset_name,'haystack_faiss.db')}"
    document_store = FAISSDocumentStore.load(
        faiss_index, sql_url=sql_url, index="document"
    )
    retriever_pt = os.path.join(DATASETS_DIR, dataset_name, "retriever.pt")
    retriever = DensePassageRetriever.load(retriever_pt, document_store=document_store)

    CURRENT_DATASET = dataset_name
    PIPELINES["QA"] = ExtractiveQAPipeline(reader, retriever)
    PIPELINES["SemanticSearch"] = DocumentSearchPipeline(retriever)


#############################################
# Endpoints
#############################################
# doc_qa_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)


@router.get("/current_dataset")
def get_current_dataset():
    return {"current_dataset": CURRENT_DATASET}


@router.get("/datasets")
def get_available_datasets():
    datasets = check_datasets()
    return {"datasets": datasets}


@router.post(
    "/models/{dataset_name}/doc-qa",
    response_model=Answers,
    response_model_exclude_unset=True,
)
def doc_qa(dataset_name: str, question_request: Question):
    # with doc_qa_limiter.run():
    start_time = time.time()
    if CURRENT_DATASET != dataset_name:
        load_model(dataset_name)
    if not PIPELINES["QA"]:
        datasets = check_datasets()
        raise HTTPException(
            status_code=500,
            detail=f"Could not get Pipeline for {dataset_name}. Available Datasets: {list(datasets)}",
        )

    results = search_documents("QA", question_request, start_time)

    return {"results": results}


@router.post(
    "/models/{dataset_name}/semanticsearch",
    response_model=Answers,
    response_model_exclude_unset=True,
)
def query(
    dataset_name: str,
    question_request: Question,
):
    # with doc_qa_limiter.run():
    start_time = time.time()
    if CURRENT_DATASET != dataset_name:
        load_model(dataset_name)
    if not PIPELINES["SemanticSearch"]:
        datasets = check_datasets()
        raise HTTPException(
            status_code=500,
            detail=f"Could not get Pipeline for {dataset_name}. Available Datasets: {list(datasets)}",
        )

    results = search_documents("SemanticSearch", question_request, start_time)

    return {"results": results}


def search_documents(
    pipeline_type, question_request, start_time
) -> List[AnswersToIndividualQuestion]:
    results = []
    for question in question_request.questions:
        pipe_args = {
            "query": question,
            "top_k_retriever": int(question_request.top_k_retriever),
        }
        if pipeline_type == "QA":
            pipe_args["top_k_reader"] = int(question_request.top_k_reader)
        result = PIPELINES[pipeline_type].run(**pipe_args)
        if pipeline_type != "QA":
            result["answers"] = result.pop("documents", None)
            for i in range(len(result["answers"])):
                result["answers"][i]["answer"] = result["answers"][i].pop("text", None)
                result["answers"][i]["score"] = (
                    result["answers"][i].pop("score", None).item()
                )
                result["answers"][i].pop("embedding")
        results.append(result)
    end_time = time.time()
    logger.info(
        json.dumps(
            {
                "request": question_request.dict(),
                "results": results,
                "time": f"{(end_time - start_time):.2f}",
            }
        )
    )
    return results
