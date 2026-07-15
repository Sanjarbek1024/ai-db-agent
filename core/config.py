# Project configuration file. All the settings and configurations for the project are defined here.

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DB_PATH = os.getenv("DB_PATH", "db/database.db")  # Default path if not set in .env

ALLOWED_TABLES = {"categories", "sellers", "listings"}  # Define allowed tables for operations

MAX_ROWS = 100  # Maximum number of rows to return in queries

GEMINI_MODEL = "gemini-3-flash-preview"