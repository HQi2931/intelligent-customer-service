"""数据库连接管理 - 强制 utf8mb4"""

import os
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session as DBSession, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:1234@localhost:3306/agent_chat",
)

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    echo=False,
    connect_args={
        "charset": "utf8mb4",
        "use_unicode": True,
    },
)

# 在引擎级别强制 utf8mb4
@event.listens_for(engine, "connect")
def _on_connect(dbapi_conn, rec):
    dbapi_conn.set_character_set("utf8mb4")


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    from db.models import Base
    Base.metadata.create_all(bind=engine)
