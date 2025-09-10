# src/apps/routes/user_route.py
from flask import Blueprint, current_app # Import current_app is still useful if you need access to app config later
from src.apps.repositories.user_repository import UserRepository
from src.apps.usecases.user_usecase import UserUseCase
from src.apps.controllers.user_controller import UserController

user_bp = Blueprint('user_bp', __name__)

# --- FIX START ---
# Initialize repository, usecase, and controller directly here
# These will be singletons for the duration of the application.
# For more complex dependency management (e.g., request-scoped),
# you'd use Flask's application context or a dependency injection library.

# We'll assume the UserRepository instance is created and managed by app.py's teardown
# and that this Blueprint can directly create the UseCase and Controller
# using a new instance of UserRepository if app.config approach isn't strictly necessary.
# However, to be consistent with app.py's attempt to store the repo instance:
# We should avoid creating a *new* repo instance here every time the module is loaded
# if app.py is already managing one for teardown.

# Best approach for this setup: Initialize once directly within the module
# and ensure the UserRepository's check_same_thread=False handles concurrency.
# If app.py is explicitly managing the UserRepository with app.config, we can pass that.

# Option 1: Initialize here as singletons, assuming UserRepository is safe to init multiple times
# (This is what you had before but without assigning to user_bp.controller_instance)
repo = UserRepository()
usecase = UserUseCase(repo)
controller = UserController(usecase)

# --- FIX END ---

# Define routes and map them to controller methods
# Now, 'controller' is a directly available variable
user_bp.route('/api/users', methods=['GET'])(controller.get_all_users)
user_bp.route('/api/user/<int:user_id>', methods=['GET'])(controller.get_user)
user_bp.route('/api/users', methods=['POST'])(controller.create_user)
user_bp.route('/api/user/<int:user_id>', methods=['PUT'])(controller.update_user)
user_bp.route('/api/user/<int:user_id>', methods=['DELETE'])(controller.delete_user)
user_bp.route('/api/search', methods=['GET'])(controller.search_users)
user_bp.route('/api/login', methods=['POST'])(controller.login_user)

# Remove the @user_bp.before_app_request block as it's no longer needed for initialization
# @user_bp.before_app_request
# def setup_dependencies():
#    repo = current_app.config.get('USER_REPOSITORY_INSTANCE')
#    if not repo:
#        raise RuntimeError("UserRepository instance not found in app.config. Ensure app.py initializes it.")
#    if not hasattr(user_bp, 'usecase_instance'):
#        user_bp.usecase_instance = UserUseCase(repo)
#        user_bp.controller_instance = UserController(user_bp.usecase_instance)
