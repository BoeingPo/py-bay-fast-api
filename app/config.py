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

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
