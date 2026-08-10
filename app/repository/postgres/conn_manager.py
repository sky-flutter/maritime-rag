import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from psycopg2 import pool
from app.utils.logger import get_logger
import threading

logger = get_logger(__name__)

class SessionScope:
    """Class-based context manager, equivalent to the @contextmanager
    generator version — commits on success, rolls back on error, always
    closes the session.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    def __enter__(self) -> Session:
        self._session = self._session_factory()
        return self._session

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        assert self._session is not None
        try:
            if exc_type is None:
                self._session.commit()
            else:
                self._session.rollback()
        finally:
            self._session.close()

class PostgresConnectionManager:
    def __init__(self, config: dict, database_url):
        self._config = config
        self.schema = 'public'
        self._connection_pool = None
        self._lock = threading.Lock()
        self._init_pool()
        self._engine = create_engine(database_url, pool_pre_ping=True)
        self._session_factory: sessionmaker[Session] = sessionmaker(
            bind=self._engine, expire_on_commit=False
        )

    def session_scope(self) -> SessionScope:
        return SessionScope(self._session_factory)

    def _init_pool(self):
        """Initialize the connection pool"""
        try:
            self._connection_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                **self._config
            )
            logger.info("Database connection pool initialized successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise Exception(f"Failed to create connection pool: {e}")

    def get_connection(self):
        """Get a connection from the pool"""
        try:
            connection = self._connection_pool.getconn()
            
            # Check if connection is still alive
            if connection and connection.closed:
                logger.warning("Connection from pool was closed, getting new one")
                connection = self._connection_pool.getconn()
            
            # Set schema if provided
            if connection and self.schema:
                with connection.cursor() as cursor:
                    cursor.execute(f'SET search_path TO {self.schema}')
                    connection.commit()

            return connection
        except psycopg2.Error as e:
            logger.error(f"Error getting connection from pool: {e}")
            # Try to reset the connection pool
            try:
                self._connection_pool.putconn(connection)
            except Exception:
                pass
            # Create a new connection directly as fallback
            try:
                connection = psycopg2.connect(**self._config)
                if self.schema:
                    cursor = connection.cursor()
                    cursor.execute(f'SET search_path TO {self.schema}')
                    cursor.close()
                    connection.commit()
                return connection
            except psycopg2.Error as retry_error:
                logger.error(f"Failed to create fallback connection: {retry_error}")
                raise Exception(f"Failed to get database connection: {retry_error}")

    def return_connection(self, connection):
        """Return a connection to the pool"""
        try:
            if connection:
                if connection.closed:
                    logger.warning("Returning closed connection to pool")
                else:
                    connection.rollback()  # Clear any remaining transactions
                self._connection_pool.putconn(connection)
        except Exception as e:
            logger.error(f"Error returning connection to pool: {e}")

    def set_schema(self, schema):
        """Set the search path to a specific schema"""
        self.schema = schema

    def close_pool(self):
        """Close all connections in the pool"""
        if self._connection_pool:
            try:
                self._connection_pool.closeall()
                logger.info("Connection pool closed")
            except Exception as e:
                logger.error(f"Error closing connection pool: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - don't close pool here since it's shared"""
        pass

