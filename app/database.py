"""Database session and model base configuration.

This module sets up a SQLAlchemy engine and session maker based on
the ``database_url`` provided via environment variables (see
``config.py``).  All ORM models should inherit from ``Base`` to
ensure that metadata is correctly shared.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import settings


# Create a SQLAlchemy engine.  Using the ``future=True`` flag enables
# SQLAlchemy 2.x style usage.  Set ``echo=False`` to silence SQL
# logging; adjust in development if you want to inspect queries.
engine = create_engine(settings.database_url, echo=False, future=True)

# SessionLocal creates new Session objects bound to our engine.  The
# ``autocommit`` and ``autoflush`` flags are set to False because we
# prefer explicit transaction control within endpoints and tasks.
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base class for declarative models.
Base = declarative_base()