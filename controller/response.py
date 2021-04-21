from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Answer(BaseModel):
    answer: Optional[str]
    question: Optional[str]
    score: Optional[float] = None
    probability: Optional[float] = None
    context: Optional[str]
    offset_start: Optional[int]
    offset_end: Optional[int]
    offset_start_in_doc: Optional[int]
    offset_end_in_doc: Optional[int]
    document_id: Optional[str] = None
    meta: Optional[Dict[str, str]]


class AnswersToIndividualQuestion(BaseModel):
    query: str
    no_ans_gap: Optional[float]
    answers: List[Optional[Answer]]

    @staticmethod
    def to_elastic_response_dsl(data: Dict[str, Any]):
        result_dsl = {"hits": {"hits": [], "total": {"value": len(data["answers"])}}}
        for answer in data["answers"]:

            record = {"_source": {k: v for k, v in dict(answer).items()}}
            record["_id"] = record["_source"].pop("document_id", None)
            record["_score"] = record["_source"].pop("score", None)

            result_dsl["hits"]["hits"].append(record)

        return result_dsl


class Answers(BaseModel):
    results: List[AnswersToIndividualQuestion]
