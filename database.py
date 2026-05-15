from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()


def _env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    return value.strip().strip('"').strip("'")


post_gres_db_name = _env("POSTGRES_DB_NAME")
post_gres_user = _env("POSTGRES_USER")
post_gres_password = _env("POSTGRES_PASSWORD")

database_url = _env("DATABASE_URL") or _env("SUPABASE_DB_URL")
if not database_url:
    database_url = (
        f"postgresql://{post_gres_user}:{post_gres_password}"
        f"@localhost:5432/{post_gres_db_name}"
    )

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

is_remote = "localhost" not in database_url and "127.0.0.1" not in database_url
connect_args = {"sslmode": "require"} if is_remote else {}

engine_kwargs = {"connect_args": connect_args, "pool_pre_ping": True}
if is_remote:
    engine_kwargs.update({"pool_size": 1, "max_overflow": 0})

engine = create_engine(database_url, **engine_kwargs)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()





Base=declarative_base()


SessionLocal=sessionmaker(autocommit=False,
    autoflush=False,
    bind=engine)