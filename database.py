from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

post_gres_db_name=os.getenv("POSTGRES_DB_NAME")
post_gres_user=os.getenv("POSTGRES_USER")
post_gres_password=os.getenv("POSTGRES_PASSWORD")

engine = create_engine(
    f"postgresql+psycopg2://{post_gres_user}:{post_gres_password}@localhost:5432/{post_gres_db_name}"
)

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