import os

from sqlalchemy import create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://nexus:nexus_dev_password@localhost:5433/nexus",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
