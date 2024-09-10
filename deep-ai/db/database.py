import os
import time
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, exc, QueuePool
from sqlmodel import SQLModel, Session

from log import log

load_dotenv()

MYSQL_DATABASE_URL = os.getenv("MYSQL_DATABASE_URL")
POOL_SIZE = 10
MAX_OVERFLOW = 20
POOL_RECYCLE = 1800  # Recycle connections after 30 minutes

engine = create_engine(
	MYSQL_DATABASE_URL,
	echo=False,
	poolclass=QueuePool,
	pool_pre_ping=True,
	pool_size=POOL_SIZE,
	max_overflow=MAX_OVERFLOW,
	pool_recycle=POOL_RECYCLE,
)


def create_db_and_tables() -> None:
	"""Create the database and tables."""
	SQLModel.metadata.create_all(engine)


def get_db_session() -> Generator[Session, None, None]:
	"""Yield a database session for the duration of a request."""
	session = Session(engine)
	try:
		yield session
		session.commit()
	except Exception as e:
		session.rollback()
		log(f"Database error during request handling: {e}")
		raise e
	finally:
		session.close()


def retry_session(retries: int = 3, delay: int = 1) -> Generator[Session, None, None]:
	"""Attempt to create a database session with retries on failure."""
	for attempt in range(retries):
		try:
			yield from get_db_session()
			break
		except exc.DBAPIError as e:
			log(f"Database connection failed, attempt {attempt + 1}: {e}")
			time.sleep(delay)
			if attempt == retries - 1:
				log("Failed to connect to the database after several attempts.")
				raise
