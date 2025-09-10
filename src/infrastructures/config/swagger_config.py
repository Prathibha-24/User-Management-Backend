

# This defines the basic information for your OpenAPI documentation
SWAGGER_URL = '/swagger'  # URL for exposing Swagger UI (e.g., y)
API_URL = '/static/swagger.json'  # Our API definition (must be reachable by Swagger UI)

# OpenAPI 3.0 Specification (as a Python dictionary)
# You would typically build this out to fully describe your API
swagger_blueprint = {
    "swagger": "2.0", # Using Swagger 2.0 (OpenAPI 2.0) for Flask-Swagger-UI simplicity.
                      # For OpenAPI 3.x, you'd use a different structure or library like Flask-RESTX.
                      # Let's stick to 2.0 for Flask-Swagger-UI's direct compatibility.
    "info": {
        "title": "User Management API",
        "description": "API for managing users, including authentication and CRUD operations.",
        "version": "1.0.0"
    },
    "host": "localhost:5000",  # Update to "user-management-apis.onrender.com" in production
    "basePath": "/",
    "schemes": [
        "http",
        "https"
    ],
    "consumes": [
        "application/json"
    ],
    "produces": [
        "application/json"
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
    "paths": {
        "/api/login": {
            "post": {
                "summary": "User Login",
                "description": "Authenticates a user and returns a JWT token.",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "email": {"type": "string", "example": "john@example.com"},
                                "password": {"type": "string", "example": "password123"}
                            },
                            "required": ["email", "password"]
                        }
                    }
                ],
                "responses": {
                    "200": {"description": "Login successful", "schema": {"type": "object", "properties": {"token": {"type": "string"}}}},
                    "400": {"description": "Bad Request", "schema": {"$ref": "#/definitions/Error"}},
                    "401": {"description": "Invalid credentials", "schema": {"$ref": "#/definitions/Error"}}
                },
                "tags": ["Auth"]
            }
        },
        "/api/users": {
            "post": {
                "summary": "Create a New User",
                "description": "Registers a new user account.",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "example": "New User"},
                                "email": {"type": "string", "example": "newuser@example.com"},
                                "password": {"type": "string", "example": "securepass"}
                            },
                            "required": ["name", "email", "password"]
                        }
                    }
                ],
                "responses": {
                    "201": {"description": "User created successfully"},
                    "400": {"description": "Bad Request (e.g., validation errors)", "schema": {"$ref": "#/definitions/Error"}},
                    "409": {"description": "Conflict (e.g., email already exists)", "schema": {"$ref": "#/definitions/Error"}},
                    "500": {"description": "Internal Server Error", "schema": {"$ref": "#/definitions/Error"}}
                },
                "tags": ["Users"]
            },
            "get": {
                "summary": "Get All Users",
                "description": "Retrieves a list of all registered users.",
                "security": [{"Bearer": []}],
                "responses": {
                    "200": {"description": "A list of users", "schema": {"type": "array", "items": {"$ref": "#/definitions/User"}}},
                    "401": {"description": "Unauthorized", "schema": {"$ref": "#/definitions/Error"}},
                    "500": {"description": "Internal Server Error", "schema": {"$ref": "#/definitions/Error"}}
                },
                "tags": ["Users"]
            }
        },
        "/api/user/{user_id}": {
            "get": {
                "summary": "Get User by ID",
                "description": "Retrieves details for a specific user.",
                "security": [{"Bearer": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "type": "integer",
                        "required": True,
                        "description": "ID of the user to retrieve"
                    }
                ],
                "responses": {
                    "200": {"description": "User found", "schema": {"$ref": "#/definitions/User"}},
                    "400": {"description": "Bad Request (e.g., invalid ID format)", "schema": {"$ref": "#/definitions/Error"}},
                    "401": {"description": "Unauthorized", "schema": {"$ref": "#/definitions/Error"}},
                    "404": {"description": "User not found", "schema": {"$ref": "#/definitions/Error"}},
                    "500": {"description": "Internal Server Error", "schema": {"$ref": "#/definitions/Error"}}
                },
                "tags": ["Users"]
            },
            "put": {
                "summary": "Update User",
                "description": "Modifies an existing user's information.",
                "security": [{"Bearer": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "type": "integer",
                        "required": True,
                        "description": "ID of the user to update"
                    },
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "example": "Updated Name"},
                                "email": {"type": "string", "example": "updated@example.com"},
                                "password": {"type": "string", "example": "newsecurepass"}
                            },
                            "minProperties": 1 # At least one property must be present for update
                        }
                    }
                ],
                "responses": {
                    "200": {"description": "User updated successfully"},
                    "400": {"description": "Bad Request (e.g., validation errors or no fields provided)", "schema": {"$ref": "#/definitions/Error"}},
                    "401": {"description": "Unauthorized", "schema": {"$ref": "#/definitions/Error"}},
                    "404": {"description": "User not found", "schema": {"$ref": "#/definitions/Error"}},
                    "409": {"description": "Conflict (e.g., email already exists)", "schema": {"$ref": "#/definitions/Error"}},
                    "500": {"description": "Internal Server Error", "schema": {"$ref": "#/definitions/Error"}}
                },
                "tags": ["Users"]
            },
            "delete": {
                "summary": "Delete User",
                "description": "Deletes a user account.",
                "security": [{"Bearer": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "type": "integer",
                        "required": True,
                        "description": "ID of the user to delete"
                    }
                ],
                "responses": {
                    "200": {"description": "User deleted successfully"},
                    "400": {"description": "Bad Request (e.g., invalid ID format)", "schema": {"$ref": "#/definitions/Error"}},
                    "401": {"description": "Unauthorized", "schema": {"$ref": "#/definitions/Error"}},
                    "404": {"description": "User not found", "schema": {"$ref": "#/definitions/Error"}},
                    "500": {"description": "Internal Server Error", "schema": {"$ref": "#/definitions/Error"}}
                },
                "tags": ["Users"]
            }
        },
        "/api/search": {
            "get": {
                "summary": "Search Users by Name",
                "description": "Searches for users whose name contains the given string (case-insensitive).",
                "security": [{"Bearer": []}],
                "parameters": [
                    {
                        "name": "name",
                        "in": "query",
                        "type": "string",
                        "required": True,
                        "description": "Partial or full name to search for"
                    }
                ],
                "responses": {
                    "200": {"description": "A list of matching users", "schema": {"type": "array", "items": {"$ref": "#/definitions/User"}}},
                    "400": {"description": "Bad Request (e.g., missing query parameter)", "schema": {"$ref": "#/definitions/Error"}},
                    "401": {"description": "Unauthorized", "schema": {"$ref": "#/definitions/Error"}},
                    "500": {"description": "Internal Server Error", "schema": {"$ref": "#/definitions/Error"}}
                },
                "tags": ["Users"]
            }
        }
    },
    "definitions": {
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"}
            },
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com"
            }
        },
        "Error": {
            "type": "object",
            "properties": {
                "error": {"type": "string", "description": "High-level error message"},
                "message": {"type": "string", "description": "Detailed error message"},
                "details": {"type": "string", "description": "Optional: More technical details for debugging"}
            }
        }
    }
}