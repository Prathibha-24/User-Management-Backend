# src\middlewares\auth_middleware.py
from functools import wraps
from flask import request, jsonify
import jwt
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret-key-change-me')

if JWT_SECRET_KEY == 'default-jwt-secret-key-change-me':
    logger.critical("JWT_SECRET_KEY not set in .env. Using default. THIS IS INSECURE FOR PRODUCTION.")

def token_required(f):
    """
    Decorator to ensure that a valid JWT token is present in the request header.
    It extracts the token, decodes it, and passes the decoded user info to the decorated function
    as a keyword argument `current_user`.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                auth_header = request.headers['Authorization']
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
            except IndexError:
                logger.warning("Malformed Authorization header: 'Bearer ' present but token missing.")
                return jsonify({'error': 'Malformed Authorization header'}), 401

        if not token:
            logger.warning("Authentication Token is missing in request headers.")
            return jsonify({'error': 'Authentication Token is missing!'}), 401

        try:
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            # Pass current_user as a keyword argument
            kwargs['current_user'] = {'id': data['id'], 'email': data['email']}
        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired token attempt from {request.remote_addr}.")
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token attempt from {request.remote_addr}: {e}")
            return jsonify({'error': f'Invalid Token: {str(e)}'}), 401
        except Exception as e:
            logger.error(f"Unexpected error during token processing from {request.remote_addr}: {e}", exc_info=True)
            return jsonify({'error': 'Token processing failed', 'details': 'An unexpected error occurred.'}), 401

        return f(*args, **kwargs) # Call the original function with modified kwargs
    return decorated