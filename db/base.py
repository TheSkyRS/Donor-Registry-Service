# engine, SessionLocal
# db/base.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # "mysql+pymysql://yl5763:yl5763@localhost:3306/donor_registry"
    "mysql+pymysql://root:yl5763@35.188.28.63:3306/donor_registry"
)

engine = create_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
