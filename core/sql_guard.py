"""
core/sql_guard.py
------------------
This module validates the AI-generated SQL query BEFORE executing it 
in the database. Its primary role is to serve as a security "filter."

Layers of Verification (Defense in Depth):
    1. The query must not be empty.
    2. Exactly ONE SQL statement is allowed (no second query hidden behind a ";").
    3. The query MUST start with a SELECT statement (validated via sqlparse).
    4. Forbidden dangerous keywords are completely blocked (DROP, DELETE, INSERT, ...).
    5. The query can ONLY reference tables listed in ALLOWED_TABLES.
    6. If no LIMIT is explicitly specified, a default LIMIT is automatically appended.

Each verification layer runs independently—ensuring that if one layer is 
somehow bypassed, the remaining layers will still catch and block the query.
"""


import re
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML, Name 

from core.config import ALLOWED_TABLES, MAX_ROWS

FORBIDDEN_KEYWORDS = [
    "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE",
    "TRUNCATE", "REPLACE", "ATTACH", "DETACH", "PRAGMA",
    "GRANT", "REVOKE", "EXEC", "EXECUTE", "VACUUM",
]

FORBIDDEN_PATTERN = re.compile(
    r"\b(" + "|".join(FORBIDDEN_KEYWORDS) + r")\b", re.IGNORECASE
)

class SQLGuardError(Exception):
    """Custom exception for SQLGuard errors."""
    
def extract_table_names(parsed_query) -> set[str]:
    """with sqlparse, extract table names from the parsed SQL query."""
    tables = set()
    tokens = list(parsed_query.flatten())

    from_seen = False
    for i, token in enumerate(tokens):
        upper_val = token.value.upper()

        if token.ttype is Keyword and upper_val in ("FROM", "JOIN"):
            from_seen = True
            continue

        if from_seen and not token.is_whitespace:
            if token.ttype is None or token.ttype in Name:
                name = token.value.strip('`"[]').lower()
                if name and re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
                    tables.add(name)
            from_seen = False

    return tables

def validate_and_prepare(raw_query: str) -> str:
    """
    Validate the AI-generated SQL query and prepare it for execution.
    """
    if not raw_query or not raw_query.strip():
        raise SQLGuardError("SQL query is empty or only whitespace.")

    query = raw_query.strip().rstrip(";").strip()

    # Only one statement is allowed
    statements = [s for s in sqlparse.split(query) if s.strip()]
    if len(statements) != 1:
        raise SQLGuardError(
            "Only one SQL statement is allowed (multiple statements found)."
        )

    parsed = sqlparse.parse(query)[0]

    # Only allow SELECT statements
    first_token = parsed.token_first(skip_cm=True)
    if first_token is None or first_token.ttype is not DML or first_token.value.upper() != "SELECT":
        raise SQLGuardError("Only SELECT statements are allowed.")

    # Dengerous keywords check
    if FORBIDDEN_PATTERN.search(query):
        raise SQLGuardError("Query contains dangerous keywords (DROP/DELETE/INSERT/...).")

    # 4. Only allowed tables can be used
    used_tables = extract_table_names(parsed)
    not_allowed = used_tables - ALLOWED_TABLES
    if not_allowed:
        raise SQLGuardError(
            f"Used not allowed tables: {', '.join(not_allowed)}. "
            f"Allowed tables: {', '.join(ALLOWED_TABLES)}"
        )

    # 5. We automatically append a LIMIT if none is specified
    if not re.search(r"\bLIMIT\s+\d+\b", query, re.IGNORECASE):
        query = f"{query} LIMIT {MAX_ROWS}"

    return query
