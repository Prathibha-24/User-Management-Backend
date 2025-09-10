import sys
import os
import json # Import json to dump the swagger_blueprint
from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint # Import Flask-Swagger-UI
from src.apps.routes.user_route import user_bp
from src.middlewares.error_middleware import register_error_handlers
from src.apps.repositories.user_repository import UserRepository
from src.infrastructures.config.swagger_config import SWAGGER_URL, API_URL, swagger_blueprint # Import your Swagger config 
from flask_cors import CORS

# Add src to the Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))




app = Flask(__name__)
CORS(app)

# --- Swagger UI Config ---
# Register Swagger UI blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "User Management API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Route to serve the OpenAPI spec JSON
@app.route(API_URL)
def swagger_spec():
    """
    Serves the OpenAPI specification as JSON.
    """
    return jsonify(swagger_blueprint)
# --- End Swagger UI Config ---


# Register other blueprints
app.register_blueprint(user_bp)

# Register custom error handlers
register_error_handlers(app)

# Store the UserRepository instance in app config for consistent access and proper teardown
with app.app_context():
    app.config['USER_REPOSITORY_INSTANCE'] = UserRepository()

# Health check endpoint
@app.route('/')
def health_check():
    """
    Health check endpoint to verify server status.
    """
    return jsonify({'status': 'success', 'message': 'Server is running'}), 200

# Teardown context to close database connection
@app.teardown_appcontext
def close_db_connection(exception=None):
    """
    Closes the database connection when the application context tears down.
    Ensures that the SQLite connection is properly closed after each request or app shutdown.
    """
    repo = app.config.get('USER_REPOSITORY_INSTANCE')
    if repo:
        repo.close_connection()
        app.config['USER_REPOSITORY_INSTANCE'] = None
        app.logger.info("Database connection closed.")
    if exception:
        app.logger.error(f"App context teardown with exception: {exception}")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
