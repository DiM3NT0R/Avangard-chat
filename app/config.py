from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_url: str
    db_name: str = "avangard"
    keycloak_url: str
    keycloak_public_url: str
    keycloak_realm: str
    keycloak_client_id: str
    groq_api_key: str
    summary_model: str = "llama-3.3-70b-versatile"
    summary_max_messages: int = 30
    summary_max_chars_per_message: int = 300

    class Config:
        env_file = "../.env"


settings = Settings()