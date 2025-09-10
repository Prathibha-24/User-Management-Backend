from flask import request, jsonify
from src.middlewares.auth_middleware import token_required
from src.apps.utils.validators import validate_user_payload
import sqlite3 # Import sqlite3 to catch IntegrityError directly
import logging # For logging internal errors

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserController:
    """
    Controller for handling user-related API requests.
    Orchestrates interaction between Flask routes, UserUseCase, and input validation.
    """
    def __init__(self, user_usecase):
        self.usecase = user_usecase

    @token_required
    def get_all_users(self, current_user):
        """
        Retrieves all users. Requires authentication.
        """
        try:
            logger.info(f"User {current_user['email']} requesting all users.")
            users = self.usecase.get_all_users()
            return jsonify([u.to_dict() for u in users]), 200
        except Exception as e:
            logger.error(f"Error getting all users: {e}", exc_info=True)
            return jsonify({'error': 'Failed to retrieve users', 'details': 'An internal server error occurred.'}), 500

    @token_required
    def get_user(self, current_user, user_id):
        """
        Retrieves a single user by ID. Requires authentication.
        """
        try:
            # Flask's route conversion handles user_id to int, but defensive check is good
            user_id = int(user_id)
            logger.info(f"User {current_user['email']} requesting user ID: {user_id}")
            user = self.usecase.get_user(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            return jsonify(user.to_dict()), 200
        except ValueError:
            return jsonify({'error': 'Invalid user ID format. Must be an integer.'}), 400
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}", exc_info=True)
            return jsonify({'error': 'Failed to retrieve user', 'details': 'An internal server error occurred.'}), 500

    def create_user(self):
        """
        Creates a new user. Does NOT require authentication.
        Includes input validation and error handling for duplicates.
        """
        data = request.get_json()
        logger.info(f"Attempting to create user with data: {data}")

        # Input validation
        errors = validate_user_payload(data, create=True)
        if errors:
            return jsonify({'errors': errors}), 400

        try:
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')

            self.usecase.create_user(name, email, password)
            logger.info(f"User {email} created successfully.")
            return jsonify({'message': 'User created successfully'}), 201 # 201 Created
        except sqlite3.IntegrityError:
            # Specific error for unique constraint violation (duplicate email)
            logger.warning(f"Attempt to create user with existing email: {email}")
            return jsonify({'error': 'User with this email already exists'}), 409 # Conflict
        except KeyError as e:
            # Should be caught by validate_user_payload, but defensive check
            logger.error(f"Missing expected data field: {e}", exc_info=True)
            return jsonify({'error': f'Missing data field: {e}'}), 400
        except Exception as e:
            logger.error(f"Failed to create user: {e}", exc_info=True)
            return jsonify({'error': 'Failed to create user', 'details': 'An internal server error occurred.'}), 500

    @token_required
    def update_user(self, current_user, user_id):
        """
        Updates an existing user by ID. Requires authentication.
        Includes input validation.
        """
        data = request.get_json()
        logger.info(f"User {current_user['email']} attempting to update user ID: {user_id} with data: {data}")

        # Input validation (for update, 'create' is False as fields are optional)
        errors = validate_user_payload(data, create=False)
        if errors:
            return jsonify({'errors': errors}), 400

        try:
            user_id = int(user_id) # Ensure user_id is integer
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')

            # At least one field should be provided for update
            if not any([name, email, password]):
                return jsonify({'error': 'No fields provided for update'}), 400

            # Get the user first to check existence
            user_exists = self.usecase.get_user(user_id)
            if not user_exists:
                return jsonify({'error': 'User not found for update'}), 404

            self.usecase.update_user(user_id, name, email, password)
            logger.info(f"User ID {user_id} updated successfully by {current_user['email']}.")
            return jsonify({'message': 'User updated successfully'}), 200
        except ValueError:
            return jsonify({'error': 'Invalid user ID format. Must be an integer.'}), 400
        except sqlite3.IntegrityError:
            logger.warning(f"Attempt to update user {user_id} with existing email: {email}")
            return jsonify({'error': 'Email already exists for another user'}), 409
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}", exc_info=True)
            return jsonify({'error': 'Failed to update user', 'details': 'An internal server error occurred.'}), 500

    @token_required
    def delete_user(self, current_user, user_id):
        """
        Deletes a user by ID. Requires authentication.
        """
        try:
            user_id = int(user_id) # Ensure user_id is integer
            logger.info(f"User {current_user['email']} attempting to delete user ID: {user_id}")
            user_exists = self.usecase.get_user(user_id)
            if not user_exists: 
                return jsonify({'error': 'User not found for deletion'}), 404  

            self.usecase.delete_user(user_id)
            logger.info(f"User ID {user_id} deleted successfully by {current_user['email']}.")
            return jsonify({'message': 'User deleted successfully'}), 200
        except ValueError:
            return jsonify({'error': 'Invalid user ID format. Must be an integer.'}), 400
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}", exc_info=True)
            return jsonify({'error': 'Failed to delete user', 'details': 'An internal server error occurred.'}), 500

    @token_required
    def search_users(self, current_user):
        """
        Searches users by name. Requires authentication.
        """
        name = request.args.get('name')
        logger.info(f"User {current_user['email']} searching for users with name: {name}")

        if not name:
            return jsonify({'error': 'Search term "name" query parameter is required'}), 400

        try:
            users = self.usecase.search_user(name)
            return jsonify([u.to_dict() for u in users]), 200
        except Exception as e:
            logger.error(f"Failed to search users by name '{name}': {e}", exc_info=True)
            return jsonify({'error': 'Failed to search users', 'details': 'An internal server error occurred.'}), 500

    def login_user(self):
        """
        Authenticates a user and returns a JWT token. Does NOT require authentication.
        """
        data = request.get_json()
        logger.info(f"Attempting login for email: {data.get('email')}")

        if not data:
            return jsonify({'error': 'No login data provided'}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        try:
            token = self.usecase.login_user(email, password)
            if token:
                logger.info(f"User {email} logged in successfully.")
                return jsonify({'token': token}), 200
            logger.warning(f"Failed login attempt for email: {email} - Invalid credentials.")
            return jsonify({'error': 'Invalid credentials'}), 401
        except Exception as e:
            logger.error(f"Login failed for email {email}: {e}", exc_info=True)
            return jsonify({'error': 'Login failed', 'details': 'An internal server error occurred.'}), 500