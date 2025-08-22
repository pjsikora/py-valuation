from sqlmodel import create_engine, SQLModel
from config.settings import settings


# Database configuration
DATABASE_URL = getattr(settings, 'database_url', 'sqlite:///sqlite.db')

# Configure engine with optimizations
engine = create_engine(
    DATABASE_URL,
    echo=getattr(settings, 'debug', False),
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)


def create_db_and_tables():
    """Initialize database tables"""
    SQLModel.metadata.create_all(engine)