from pydantic_settings import BaseSettings
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    google_api_key:str

    
    class Config:
        env_file = os.path.join(BASE_DIR, ".env")
        
env = Settings()

if not env.google_api_key:
    raise ValueError("GOOGLE_API_KEY does not exist. Please provide it via a .env file or environment variable.")

