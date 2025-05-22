from drf_yasg import openapi

SIMPLE_LOGIN_VIEW_SCHEMA = {
    "operation_summary": "User Login",
    "operation_description": (
        "Authenticates an existing user. "
        "Requires `username` and `password`. "
        "Returns access & refresh JWT tokens on success."
    ),
    "request_body": openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["username", "password"],
        properties={
            "username": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Your registered username",
                example="testuser1",
            ),
            "password": openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_PASSWORD,
                description="Your account password",
                example="P@$$wOrd123",
            ),
        },
    ),
    "responses": {
        200: openapi.Response(description="OK – returns JWT tokens"),
        401: openapi.Response(description="Invalid credentials"),
    },
    "tags": ["Authentication"],
}
