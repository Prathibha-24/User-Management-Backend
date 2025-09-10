import sqlite3
from src.apps.models.user_model import User
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    """
    Handles data access operations for the User entity using SQLite.
    Manages database connection and CRUD operations.
    """
    def __init__(self):
        # Use check_same_thread=False for Flask dev server to allow multiple threads
        # to use the same connection. For production, consider connection pools.
        try:
            self.conn = sqlite3.connect('users.db', check_same_thread=False)
            self.conn.row_factory = sqlite3.Row # Allows accessing columns by name
            self.create_table()
            logger.info("Database connection established and table checked.")
        except sqlite3.Error as e:
            logger.critical(f"Failed to connect to database: {e}", exc_info=True)
            raise # Re-raise to prevent app from starting without DB

    def _execute_query(self, query, params=(), fetch_one=False, fetch_all=False):
        """
        Helper method to execute SQL queries with error handling and transaction management.
        """
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit() # Commit changes after successful execution
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            return None
        except sqlite3.IntegrityError as e:
            self.conn.rollback() # Rollback on integrity error (e.g., unique constraint violation)
            logger.error(f"SQLite Integrity Error: {e} | Query: {query} | Params: {params}", exc_info=True)
            raise # Re-raise for controller to handle specific error
        except sqlite3.Error as e:
            self.conn.rollback() # Rollback on any other SQLite error
            logger.error(f"SQLite Database Error: {e} | Query: {query} | Params: {params}", exc_info=True)
            raise Exception(f"Database operation failed: {e}") from e # Wrap and re-raise
        finally:
            if cursor:
                cursor.close()

    def create_table(self):
        """
        Creates the users table if it doesn't exist.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        '''
        self._execute_query(query)

    def get_all_users(self):
        """
        Retrieves all users from the database.
        Returns a list of User objects.
        """
        rows = self._execute_query('SELECT id, name, email, password FROM users', fetch_all=True)
        return [User(row['id'], row['name'], row['email'], row['password']) for row in rows] if rows else []

    def get_user_by_id(self, user_id):
        """
        Retrieves a single user by their ID.
        Returns a User object or None if not found.
        """
        row = self._execute_query('SELECT id, name, email, password FROM users WHERE id=?', (user_id,), fetch_one=True)
        return User(row['id'], row['name'], row['email'], row['password']) if row else None

    def create_user(self, name, email, password):
        """
        Inserts a new user into the database.
        Expected to raise sqlite3.IntegrityError if email already exists (handled in controller).
        """
        query = 'INSERT INTO users (name, email, password) VALUES (?, ?, ?)'
        self._execute_query(query, (name, email, password))

    def update_user(self, user_id, name=None, email=None, password=None):
        """
        Updates an existing user's details. Only updates provided (non-None) fields.
        Raises sqlite3.IntegrityError if new email already exists.
        """
        updates = []
        params = []
        if name is not None:
            updates.append('name=?')
            params.append(name)
        if email is not None:
            updates.append('email=?')
            params.append(email)
        if password is not None:
            updates.append('password=?')
            params.append(password)

        if not updates:
            logger.info(f"No fields provided to update for user ID: {user_id}")
            return # No fields to update

        query = f'UPDATE users SET {", ".join(updates)} WHERE id=?'
        params.append(user_id)
        self._execute_query(query, tuple(params))


    def delete_user(self, user_id):
        """
        Deletes a user from the database by ID.
        """
        query = 'DELETE FROM users WHERE id=?'
        self._execute_query(query, (user_id,))

    def get_user_by_email(self, email):
        """
        Retrieves a single user by their email address.
        Returns a User object or None if not found.
        """
        row = self._execute_query('SELECT id, name, email, password FROM users WHERE email=?', (email,), fetch_one=True)
        return User(row['id'], row['name'], row['email'], row['password']) if row else None

    def search_users_by_name(self, name):
        """
        Searches for users whose name contains the given string (case-insensitive).
        Returns a list of User objects.
        """
        query = 'SELECT id, name, email, password FROM users WHERE LOWER(name) LIKE ?'
        rows = self._execute_query(query, ('%' + name.lower() + '%',), fetch_all=True)
        return [User(row['id'], row['name'], row['email'], row['password']) for row in rows] if rows else []

    def close_connection(self):
        """
        Closes the database connection.
        """
        if self.conn:
            self.conn.close()
            logger.info("UserRepository database connection explicitly closed.")