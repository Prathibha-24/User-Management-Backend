import jwt
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv() # Load environment variables from .env

# Get secret keys from environment variables
# Provide strong default values or ensure they are always set in .env
SECRET_KEY = os.getenv('SECRET_KEY', 'default-flask-secret-key-change-me')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret-key-change-me')

if SECRET_KEY == 'default-flask-secret-key-change-me':
    logger.warning("SECRET_KEY not set in .env. Using default. Please set a strong, random key.")
if JWT_SECRET_KEY == 'default-jwt-secret-key-change-me':
    logger.warning("JWT_SECRET_KEY not set in .env. Using default. Please set a strong, random key.")

class UserUseCase:
    """
    Business logic layer for User operations.
    Interacts with UserRepository and handles password hashing/JWT generation.
    """
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def get_all_users(self):
        """
        Fetches all user records.
        """
        return self.user_repo.get_all_users()

    def get_user(self, user_id):
        """
        Fetches a single user by ID.
        """
        return self.user_repo.get_user_by_id(user_id)

    def create_user(self, name, email, password):
        """
        Creates a new user with a hashed password.
        Raises ValueError if required fields are missing.
        """
        if not all([name, email, password]):
            # This should ideally be caught by validator, but defensive check
            raise ValueError("All fields (name, email, password) are required to create a user.")
        # Use pbkdf2:sha256 as a more secure default method for hashing
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        self.user_repo.create_user(name, email, hashed_password)

    def update_user(self, user_id, name=None, email=None, password=None):
        """
        Updates an existing user's details. Only updates provided fields.
        Password will be re-hashed if provided.
        Raises ValueError if no fields are provided for update.
        """
        if not any([name, email, password]):
            raise ValueError("At least one field (name, email, or password) must be provided for update.")

        # Hash password only if it's provided for update
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256') if password else None
        self.user_repo.update_user(user_id, name, email, hashed_password)

    def delete_user(self, user_id):
        """
        Deletes a user by ID.
        """
        self.user_repo.delete_user(user_id)

    def search_user(self, name):
        """
        Searches for users by name.
        """
        return self.user_repo.search_users_by_name(name)

    def login_user(self, email, password):
        """
        Authenticates a user and generates a JWT token upon successful login.
        Returns the token string or None if authentication fails.
        """
        user = self.user_repo.get_user_by_email(email)
        if user and check_password_hash(user.password, password):
            # Using JWT_SECRET_KEY for signing tokens for clarity and security separation
            token = jwt.encode(
                {'id': user.user_id, 'email': user.email},
                JWT_SECRET_KEY,
                algorithm='HS256'
            )
            # jwt.encode returns bytes, often needs to be decoded for Flask jsonify
            return token
        return None