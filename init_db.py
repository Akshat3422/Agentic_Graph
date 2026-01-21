from database import engine, Base
import models   # ⚠️ YE LINE SABSE IMPORTANT


def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()