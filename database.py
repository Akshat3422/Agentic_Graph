from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base


engine = create_engine(
    "postgresql+psycopg2://postgres:Akshat3422%40@localhost:5432/postgres",
    echo=True,
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