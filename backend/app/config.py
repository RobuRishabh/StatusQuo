from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://statusquo:statusquo@localhost:5432/statusquo"
    secret_key: str = "change-me-to-a-random-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://localhost:8000/api/auth/github/callback"

    github_cloud_token: str = ""
    github_enterprise_url: str = ""
    github_enterprise_token: str = ""

    gitlab_cloud_token: str = ""
    gitlab_self_url: str = ""
    gitlab_self_token: str = ""

    jira_base_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""

    confluence_base_url: str = ""
    confluence_email: str = ""
    confluence_api_token: str = ""

    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    upload_dir: str = "./uploads"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
