from flask import jsonify, request
from werkzeug.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """
    Registers custom error handlers for common HTTP status codes and general exceptions.
    """

    @app.errorhandler(404)
    def not_found(error):
        """Handles 404 Not Found errors."""
        logger.warning(f"404 Not Found: {request.url}")
        return jsonify({'error': 'Resource Not Found', 'message': str(error)}), 404

    @app.errorhandler(400)
    def bad_request(error):
        """Handles 400 Bad Request errors."""
        # This typically catches Flask's internal parsing errors (e.g., malformed JSON).
        # Specific validation errors from controllers should return 400 with a custom message.
        logger.warning(f"400 Bad Request: {request.url} - {error}")
        return jsonify({'error': 'Bad Request', 'message': str(error)}), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handles 405 Method Not Allowed errors."""
        logger.warning(f"405 Method Not Allowed: {request.method} on {request.url}")
        return jsonify({'error': 'Method Not Allowed', 'message': str(error)}), 405

    @app.errorhandler(500)
    def internal_error(error):
        """Handles 500 Internal Server Error."""
        # Log the actual error for debugging in production
        logger.exception(f"500 Internal Server Error: {error}") # Logs traceback
        return jsonify({'error': 'Internal Server Error', 'message': 'Something went wrong on our side.'}), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """
        Catch all Werkzeug HTTPExceptions (e.g., 401, 403, etc.) not specifically handled.
        This provides a consistent JSON error response for these exceptions.
        """
        logger.warning(f"HTTP Exception {e.code}: {e.description}")
        response = e.get_response()
        response.data = jsonify({
            "code": e.code,
            "name": e.name,
            "description": e.description,
            "message": "An HTTP error occurred."
        }).get_data(as_text=True)
        response.content_type = "application/json"
        return response

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        """
        Catch-all for any uncaught exceptions. This prevents the server from crashing
        and provides a generic 500 error message to the client while logging details.
        """
        logger.exception(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred', 'message': 'Please try again later.'}), 500