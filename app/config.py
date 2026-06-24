from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # PostgreSQL
    postgres_user: str = "appuser"
    postgres_password: str = "apppassword"
    postgres_db: str = "appdb"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_expire_minutes: int = 1440  # 24 hours

    # DynamoDB Local
    dynamodb_endpoint: str = "http://localhost:8000"
    aws_access_key_id: str = "local"
    aws_secret_access_key: str = "local"
    aws_default_region: str = "us-east-1"

    # CORS — localhost for dev, bay-preact-bo for the deployed ts-preact-bay frontend
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://bay-preact-bo.k3s.porrapatbo.site",
    ]

    # Auth cookie — flip to True once served over HTTPS in production
    cookie_secure: bool = False

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
