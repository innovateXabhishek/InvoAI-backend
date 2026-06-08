"""Application configuration and settings.

The settings class uses Pydantic's BaseSettings to load values from
environment variables.  This makes it easy to override defaults in
development, staging and production environments while keeping a
centralised configuration object.
"""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Configuration values loaded from the environment.

    - ``database_url``: SQLAlchemy connection string to your PostgreSQL
      or other relational database.
    - ``redis_broker_url``: URL for the Celery broker (typically
      pointing to a Redis instance).
    - ``openai_api_key``: API key for the OpenAI vision model; leave
      empty in development if you haven't provisioned one yet.
    - ``model_name``: Identifier for the LLM/vision model you want to
      use when extracting invoice data or answering questions.
    """

    database_url: str = (
        "postgresql+psycopg2://invo_user:invo_pass@localhost:5432/invo_db"
    )
    redis_broker_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    model_name: str = "gpt-4o"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()