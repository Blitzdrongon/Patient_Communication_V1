"""
Configuration for Patient Communitation
"""

import os
from typing import Optional, List
from pydantic import Field, field_validator, AliasChoices
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """ Application Settings"""

    #API keys
    google_api_key: str = Field(
        ..., 
        description="Google API key for vision LLM",
        validation_alias=AliasChoices("GOOGLE_API_KEY", "GOOGLE_API", "google_api_key", "google_api")
    )
    elevenlabs_api_key: str = Field(..., description="ElevenLabs API key for TTS")
    
    # API Configuration
    elevenlabs_base_url: str = Field(default="https://api.elevenlabs.io/v1", description="ElevenLabs API base URL")

    #applicaition config
    app_name: str = Field(default="Patient Communication",description="Application for patient.")
    app_version:str =  Field(default="1.0.0",description="Application version")
    debug: bool = Field(default=False,description="debug mode")
    log_level: str = Field(default="INFO",description="log level")


    #Language config 
    default: str = Field(default="en",description="Default language")
    supported_language: str =Field(default="en,kn,hn",description="supported languages")

    #Model config
    text_model: str = Field(default="google/medgemma-4b-it", description="Text generation model")
    vision_model: str = Field(default="gemini-flash-2.5", description="Vision model")
    tts_voice_id: str = Field(default="21m00Tcm4TlvDq8ikWAM", description="ElevenLabs voice ID")

    #memory config
    sqlite_database_url: str = Field(default="sqlite:///./raithamithra.db", description="SQLite database URL")
    

    #validation - updated for Pydantic V2
    @field_validator('google_api_key')
    @classmethod
    def validate_required_api_keys(cls,v:str,info)-> str:
        if v in [f"your_{info.field_name}_here","test_key_validation"]:
            return v
        if not v:
            raise ValueError(f"{info.field_name} is required")
        return v
    
    # Updated for Pydantic V2
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


#Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get Application Settings"""
    return settings


