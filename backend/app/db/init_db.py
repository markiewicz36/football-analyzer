from ..models.models import create_tables
from .database import engine, SessionLocal
import logging

logger = logging.getLogger(__name__)

def init_db():
    """
    Initialize the database by creating all tables.
    """
    try:
        create_tables(engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_session():
    """
    Create a new database session.
    """
    return SessionLocal()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    logger.info("Database initialization completed.")