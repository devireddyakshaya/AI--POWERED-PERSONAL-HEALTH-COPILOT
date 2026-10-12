"""
Database connection and session management for MediMitra AI.
Uses SQLite for local, privacy-first hackathon operation.
"""
import logging
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import DATABASE_URL

logger = logging.getLogger("MediMitra.db")

# For SQLite, ensure connect_args allows multi-threading in FastAPI
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

# Enable foreign keys for SQLite
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Additive schema changes applied to existing SQLite databases that were created
# before a column existed. `create_all` never alters existing tables, so this
# keeps older local databases working without a destructive reset.
_ADDITIVE_COLUMNS = {
    "documents": {
        "specialty": "VARCHAR(50) DEFAULT 'General Medicine'",
    },
    "patients": {
        "external_patient_id": "VARCHAR(80)",
    },
}


def run_lightweight_migrations() -> None:
    """Adds any missing additive columns to existing tables (SQLite-safe)."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    with engine.begin() as conn:
        for table, columns in _ADDITIVE_COLUMNS.items():
            if table not in existing_tables:
                continue
            present = {col["name"] for col in inspector.get_columns(table)}
            for column, ddl in columns.items():
                if column not in present:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))
                    logger.info(f"Migrated: added {table}.{column}")


def get_db():
    """Dependency that provides a database session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
