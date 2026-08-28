import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str = 'dummy_key'
    model_name: str = 'gemini-1.5-pro'
    
    # Pathlib absolute paths relative to project root
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / 'data'
    kb_dir: Path = base_dir / 'knowledge-base'
    chroma_db_dir: Path = base_dir / 'chroma_db'

    class Config:
        env_file = '.env'

settings = Settings()
