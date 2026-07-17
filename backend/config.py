from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./fitness_studio.db"
    secret_key: str = "dev-secret-key"
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_server: str = "smtp.gmail.com"
    mail_port: int = 587
    mail_from_name: str = "מכון כושר"
    frontend_url: str = "http://localhost:4200"

    class Config:
        env_file = ".env"


settings = Settings()
