class User:
    """
    Represents a User entity.
    """
    def __init__(self, user_id, name, email, password):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password

    def to_dict(self):
        """
        Converts the User object to a dictionary, excluding the password for security.
        """
        return {
            'id': self.user_id,
            'name': self.name,
            'email': self.email
        }