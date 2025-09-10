import re

def validate_user_payload(data, create=False):
    """
    Validates user data payload for creation or update.
    Args:
        data (dict): The incoming JSON data.
        create (bool): True if validating for user creation (all relevant fields required),
                       False for update (fields are optional).
    Returns:
        list: A list of error messages, empty if validation passes.
    """
    errors = []
    if not data:
        errors.append("No data provided in the request body.")
        return errors

    # Check for required fields on creation
    if create:
        if not data.get("name"):
            errors.append("Name is required.")
        if not data.get("email"):
            errors.append("Email is required.")
        if not data.get("password"):
            errors.append("Password is required.")
        # If any of the above are missing, stop email/password format checks
        # as they would also fail and create redundant errors.
        if errors:
            return errors

    # Validate email format if provided (or if required and present for creation)
    if "email" in data and data["email"]:
        if not isinstance(data["email"], str):
            errors.append("Email must be a string.")
        elif not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", data["email"]):
            errors.append("Invalid email format.")

    # Validate password if provided (or if required and present for creation)
    if "password" in data and data["password"]:
        if not isinstance(data["password"], str):
            errors.append("Password must be a string.")
        elif len(data["password"]) < 8: # Example: Minimum 8 characters
            errors.append("Password must be at least 8 characters long.")
        # Add more complex password rules if needed (e.g., contains number, special char)

    # Validate name if provided (or if required and present for creation)
    if "name" in data and data["name"]:
        if not isinstance(data["name"], str):
            errors.append("Name must be a string.")
        elif len(data["name"].strip()) == 0:
            errors.append("Name cannot be empty.")

    return errors