# src\apps\config.py

# It's recommended to load sensitive keys from environment variables directly
# in the modules that use them (e.g., usecase, middleware).
# This file can be used for other non-sensitive, application-wide configurations.

SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
# SECRET_KEY and JWT_SECRET_KEY are now primarily loaded via dotenv in respective modules.
# You can keep these as fallback defaults or remove them if entirely relying on .env.
# SECRET_KEY = 'your-secret-key'
# JWT_SECRET_KEY = 'your-jwt-secret-key'