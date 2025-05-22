from drf_yasg import openapi
from rest_framework import status

AuthResponseSerializer = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "access": openapi.Schema(type=openapi.TYPE_STRING),
        "refresh": openapi.Schema(type=openapi.TYPE_STRING),
    },
)


USER_LOGIN_SCHEMA = {
    "operation_id": "user_login",
    "operation_summary": "User Login",
    "operation_description": (
        "Authenticates an existing user with their username and password. "
        "Upon successful authentication, it returns JWT access and refresh tokens."
    ),
    "request_body": openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["username", "password"],
        properties={
            "username": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Registered username of the user.",
                example="testuser",
            ),
            "password": openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_PASSWORD,
                description="Password for the user account.",
                example="P@$$wOrd123",
            ),
        },
    ),
    "responses": {
        status.HTTP_200_OK: openapi.Response(
            description="OK – Authentication successful. JWT tokens are returned.",
            schema=AuthResponseSerializer,
            examples={
                "application/json": {
                    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE2NDc...",
                    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxNz...",
                }
            },
        ),
        status.HTTP_401_UNAUTHORIZED: openapi.Response(
            description="Unauthorized – Authentication failed due to invalid credentials or other errors.",
            examples={
                "application/json (Invalid Credentials)": {
                    "authorization": ["Invalid credentials provided."]
                },
                "application/json (Generic Error)": {"authorization": "error"},
            },
        ),
    },
    "tags": ["Authentication"],
}
