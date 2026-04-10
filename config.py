import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    DB_PATH = os.environ.get("DB_PATH", "memory.db")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
