from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "local"
    app_name: str = "memory-rag-be"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "memory_rag"
    db_password: str = ""
    db_name: str = "memory_rag"
    database_url: str = ""

    llm_provider: Literal["mock", "gemini_api", "vertex", "openai"] = "mock"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"
    vertex_project_id: str = ""
    vertex_location: str = "us-central1"
    vertex_model_name: str = "gemini-1.5-flash"
    openai_api_key: str = ""

    vector_store_provider: Literal["none", "chroma", "vertex"] = "none"
    vertex_vector_index_id: str = ""
    vertex_vector_endpoint_id: str = ""
    vertex_vector_deployed_index_id: str = ""

    gcs_bucket_name: str = ""
    google_application_credentials: str = ""

    enable_cloud_logging: bool = False
    log_to_file: bool = True
    log_dir: str = "logs"
    log_json: bool = False
    enable_memory_update: bool = True
    enable_guardrail: bool = True
    enable_quality_loop: bool = True
    enable_agent_tools: bool = True
    quality_max_retries: int = 2
    quality_confidence_threshold: float = 0.5

    chroma_persist_dir: str = ".chroma_memory_rag"

    active_prompt_version: str = "v0.3"
    recent_swing_limit: int = 5
    recent_message_limit: int = 20

    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "memory-rag-demo"
    langsmith_endpoint: str = "https://api.smith.langchain.com"

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def file_logging_enabled(self) -> bool:
        """Local timestamped log files; disabled for prod and Cloud Logging."""
        if self.enable_cloud_logging:
            return False
        if self.app_env.lower() == "prod":
            return False
        return self.log_to_file

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def vertex_vector_search_configured(self) -> bool:
        return bool(
            self.vertex_project_id
            and self.vertex_vector_index_id
            and self.vertex_vector_endpoint_id
            and self.vertex_vector_deployed_index_id
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
