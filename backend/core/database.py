import psycopg2
import psycopg2.pool

# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQLの接続情報
SQLALCHEMY_DATABASE_URL = "postgresql://muneyukisato:@localhost:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 全てのモデルが継承する親クラス（これの .metadata に設計図が集まる）
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 接続プール用のグローバル変数
# pool: psycopg2.pool.ThreadedConnectionPool = None

# def init_db_pool():
#     global pool
#     pool = psycopg2.pool.ThreadedConnectionPool(
#         minconn=1,
#         maxconn=10,
#         host="localhost",
#         database="postgres",
#         user="muneyukisato",
#         password="",
#         port="5432"
#     )

# def close_db_pool():
#     global pool
#     if pool:
#         pool.closeall()

# def get_db():
#     """リクエストごとにプールから接続を取得し、レスポンス返却時にプールへ戻す"""
#     conn = pool.getconn()
#     try:
#         yield conn
#         conn.commit()
#     except Exception:
#         conn.rollback()
#         raise
#     finally:
#         pool.putconn(conn)