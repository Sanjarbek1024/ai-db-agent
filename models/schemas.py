"""
This module contains the Pydantic models used for request and response validation in the application.
"""

from typing import Any
from pydantic import BaseModel, Field

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, description="User's question to be answered by the LLM.")


class QueryResponse(BaseModel):
    success: bool
    question: str
    generated_sql: str | None = None
    columns: list[str] = []
    rows: list[dict[str, Any]] = []
    row_count: int = 0
    error: str | None = None