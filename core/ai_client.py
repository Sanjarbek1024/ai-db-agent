# Description in english

"""
core/ai_client.py
-------------------

This file contains the AI client implementation for interacting with the Gemini API.
"""

from google import genai
from google.genai import types
from core.config import GEMINI_API_KEY, GEMINI_MODEL, ALLOWED_TABLES, MAX_ROWS

client = genai.Client(api_key=GEMINI_API_KEY)  # Initialize the Gemini API client with the provided API key

db_schema_description = """
Database Schema (SQLite):

categories(id INTEGER PRIMARY KEY, name TEXT)
sellers(id INTEGER PRIMARY KEY, name TEXT, city TEXT, rating REAL)
listings(
    id INTEGER PRIMARY KEY,
    title TEXT,
    price INTEGER,
    category_id INTEGER,   -- connected to categories.id
    seller_id INTEGER,     -- connected to sellers.id
    location TEXT,
    created_at TEXT,       -- In 'YYYY-MM-DD' format
    updated_at TEXT,       -- In 'YYYY-MM-DD' format
    is_active INTEGER      -- 1 = active, 0 = inactive
)
"""

system_instruction = f"""You are a database assistant. The user will ask a question in natural language. Your task is to write a single, safe SQLite SELECT query that answers the question and call the `run_sql_query` function. 

Strict rules:
- Write ONLY SELECT queries. Never write INSERT, UPDATE, DELETE, or DROP.
- Use ONLY the following tables: {', '.join(sorted(ALLOWED_TABLES))}
- Even if the question is ambiguous, suggest the most logical SELECT query.
- Use LIMIT if necessary to restrict the results.

{db_schema_description}
"""

run_sql_query_function = {
    "name": "run_sql_query",
    "description": "Executes a safe SQLite SELECT query and returns the results.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A safe SQLite SELECT query to execute. Reminder: Only SELECT queries are allowed."
            }
        },
        "required": ["query"]
}
}

class AIClientError(Exception):
    """Custom exception class for AIClient errors."""
    
    
def generate_sql(question: str) -> str:
    """Generates a safe SQLite SELECT query based on the user's natural language question using the Gemini API."""
    
    if client is None:
        raise AIClientError("Gemini API client is not initialized. Please check your API key.")
    
    tool = types.TOOL(function_declaration=run_sql_query_function)
    
    response = client.model.generate_content(
        model=GEMINI_MODEL,
        contents=question,
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[tool],
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="ANY")
            ),
            temperature=0, # Set temperature to 0 for deterministic output
        ),
    )
    
    candidates = response.candidates or []
    if not candidates or not candidates[0].content.parts:
        raise AIClientError("Couldn't generate a valid response from the Gemini API.")

    
    for part in candidates[0].content.parts:
        fn_call = getattr(part, "function_call", None)
        if fn_call and fn_call.name == "run_sql_query":
            query = fn_call.args.get("query")
            if query:
                return query
            
    raise AIClientError("No valid SQL query found in the Gemini API response.")