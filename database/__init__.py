# database/__init__.py
# Ky fajll e bën folderin 'database' një Python package

from .database import get_db_connection, execute_query

__all__ = ['get_db_connection', 'execute_query']
