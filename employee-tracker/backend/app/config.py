import os


class Settings:
    mongo_url: str = os.environ.get("MONGO_URL", "mongomock://localhost/employee_tracker")
    db_name: str = os.environ.get("DB_NAME", "employee_tracker")
    jwt_secret: str = os.environ.get("JWT_SECRET", "dev-secret-change-me-before-deploying-32bytes")
    jwt_alg: str = "HS256"
    jwt_lifetime_hours: int = 12
    bcrypt_cost: int = 12
    default_max_accuracy_m: float = 100.0
    stale_capture_seconds: int = 5 * 60
    auth_rate_limit_per_min: int = 10
    public_ip_rate_limit_per_min: int = 30
    public_token_rate_limit_per_min: int = 5


settings = Settings()
