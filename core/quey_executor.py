"""
core/query_executor.py
------------------------
Get the SQL query from the LLM, validate it, and execute it in the database.
"""

import sqlite3
from core.config import DB_PATH

def run_query(query: str) -> dict:
    """
    Execute the validated SQL query in the SQLite database and return the results.
    
    Returns:
    {
        "success": True,
        "columns": [...],
        "rows": [{...}, {...}],
        "row_count": N
    }
    or
    {
        "success": False, 
        "error": "..."
    }
    """
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        conn.execute("PRAGMA query_only = ON;")
        
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        result_rows = [dict(row) for row in rows]
        
        return {
            "success": True,
            "columns": columns,
            "rows": result_rows,
            "row_count": len(result_rows),
        }
        
    except sqlite3.Error as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()