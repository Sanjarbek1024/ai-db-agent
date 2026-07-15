""" 
main.py
-----------------
This module contains the main entry point for the application. It initializes the necessary components and starts the
"""

import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from core.ai_client import generate_sql, AIClientError
from core.sql_guard import validate_and_prepare, SQLGuardError
from core.query_executor import run_query
from core.config import ALLOWED_TABLES
from models.schemas import QuestionRequest, QueryResponse

app = FastAPI(title="AI SQL Agent")

BASE_DIR = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "allowed_tables": sorted(ALLOWED_TABLES)},
    )


@app.post("/ask", response_model=QueryResponse)
def ask(payload: QuestionRequest):
    question = payload.question.strip()

    # 1. Generate SQL from the question using the LLM
    try:
        raw_sql = generate_sql(question)
    except AIClientError as e:
        return QueryResponse(success=False, question=question, error=str(e))

    # 2. Validate and prepare the SQL query
    try:
        safe_sql = validate_and_prepare(raw_sql)
    except SQLGuardError as e:
        return QueryResponse(
            success=False, question=question, generated_sql=raw_sql, error=str(e)
        )

    # 3. Execute the query in the database
    result = run_query(safe_sql)

    if not result["success"]:
        return QueryResponse(
            success=False,
            question=question,
            generated_sql=safe_sql,
            error=result["error"],
        )

    return QueryResponse(
        success=True,
        question=question,
        generated_sql=safe_sql,
        columns=result["columns"],
        rows=result["rows"],
        row_count=result["row_count"],
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)