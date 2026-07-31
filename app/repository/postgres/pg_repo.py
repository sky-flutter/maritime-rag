from typing import Generator, List, Tuple, Union, Dict
from jinja2 import Environment, select_autoescape
from api.utils.logger import get_logger
from app.repository.postgres.connection_manager import PostgresConnectionManager

logger = get_logger(__name__)


class PostgresRepository:
    def __init__(self, connection_manager: PostgresConnectionManager):
        """
        Initialize PostgresRepository with a database connection manager.
        
        Args:
            connection_manager: A database connection manager object
        """
        self.connection_manager = connection_manager
        self.env = Environment(autoescape=select_autoescape(
            enabled_extensions=('html', 'sql')))

    def _execute_query(self, query: str, params: dict = None):
        """
        Execute a query and return the cursor and connection.
        
        Args:
            query: SQL query string
            params: Optional parameters for the query
            
        Returns:
            Tuple of (cursor, connection)
        """
        conn = None
        try:
            conn = self.connection_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor, conn
        except Exception as e:
            if conn:
                self.connection_manager.return_connection(conn)
            logger.error(f"Error executing query: {e}")
            raise

    def _close_cursor_and_return_connection(self, cursor, conn):
        """Close cursor and return connection to pool"""
        try:
            if cursor:
                cursor.close()
        except Exception as e:
            logger.error(f"Error closing cursor: {e}")
        finally:
            if conn:
                self.connection_manager.return_connection(conn)

    def fetch_all(self, query: str, params: dict = None, as_dict: bool = False) -> Union[List[Tuple], List[Dict]]:
        """
        Fetch all results from a query.
        
        Args:
            query: SQL query string
            params: Optional parameters for the query
            as_dict: If True, return results as list of dictionaries
            
        Returns:
            List of tuples containing the query results, or list of dicts if as_dict=True
        """
        cursor = None
        conn = None
        try:
            cursor, conn = self._execute_query(query, params)
            results = cursor.fetchall()
            if as_dict and results:
                columns = [desc[0] for desc in cursor.description]
                results = [dict(zip(columns, row)) for row in results]
            return results
        finally:
            self._close_cursor_and_return_connection(cursor, conn)

    def fetch_one(self, query: str, params: dict = None) -> Tuple:
        """
        Fetch a single result from a query.
        
        Args:
            query: SQL query string
            params: Optional parameters for the query
            
        Returns:
            Tuple containing the single query result, or None if no results
        """
        cursor = None
        conn = None
        try:
            cursor, conn = self._execute_query(query, params)
            result = cursor.fetchone()
            return result
        finally:
            self._close_cursor_and_return_connection(cursor, conn)

    def fetch_in_batches(self, query: str, batch_size: int, params: dict = None) -> Generator[List[Tuple], None, None]:
        """
        Fetch results from a query in batches.
        
        Args:
            query: SQL query string
            batch_size: Number of records to fetch per batch
            params: Optional parameters for the query
            
        Yields:
            List of tuples containing batch results
        """
        cursor = None
        conn = None
        try:
            cursor, conn = self._execute_query(query, params)
            while True:
                batch = cursor.fetchmany(size=batch_size)
                if not batch:
                    break
                yield batch
        finally:
            self._close_cursor_and_return_connection(cursor, conn)

    def execute(self, query: str, params: dict = None) -> int:
        """
        Execute a query that doesn't return results (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query string
            params: Optional parameters for the query
            
        Returns:
            Number of affected rows
        """
        cursor = None
        conn = None
        try:
            cursor, conn = self._execute_query(query, params)
            conn.commit()
            return cursor.rowcount
        finally:
            self._close_cursor_and_return_connection(cursor, conn)

    def execute_many(self, query: str, params_list: List[dict]) -> int:
        """
        Execute a query multiple times with different parameters.
        
        Args:
            query: SQL query string
            params_list: List of parameter dictionaries
            
        Returns:
            Number of affected rows
        """
        cursor = None
        conn = None
        try:
            conn = self.connection_manager.get_connection()
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        finally:
            self._close_cursor_and_return_connection(cursor, conn)

    def close(self):
        """
        Close the database connection pool.
        Note: This is generally not needed in a pool-based setup.
        """
        if self.connection_manager:
            self.connection_manager.close_pool()
