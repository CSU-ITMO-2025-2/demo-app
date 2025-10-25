import os


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/todo_db")


settings = Settings()
