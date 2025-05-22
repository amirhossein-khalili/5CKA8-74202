from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import (
    AuthResponseSerializer,
    SignInSerializer,
    SignUpSerializer,
)
from accounts.services import AuthenticationFacadeService

_facade = AuthenticationFacadeService()


class SignUpView(APIView):
    """
    post:
    Register a new user with a username and password, returning JWT tokens.
    """

    permission_classes = []

    @swagger_auto_schema(
        operation_summary="User Registration",
        operation_description=(
            "Creates a new user account. "
            "Requires `username` (string) and `password` (string). "
            "Returns access & refresh JWT tokens on success."
        ),
        request_body=SignUpSerializer,
        responses={
            201: openapi.Response(
                description="Created – returns JWT tokens",
                schema=AuthResponseSerializer,
            ),
            400: "Validation errors (e.g. password too weak, username taken)",
        },
    )
    def post(self, request):
        tokens = _facade.sign_up(request.data, context={"request": request})
        return Response(tokens, status=status.HTTP_201_CREATED)


class SignInView(APIView):
    """
    post:
    Authenticate a user and return JWT tokens.
    """

    permission_classes = []

    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description=(
            "Authenticates an existing user. "
            "Requires `username` and `password`. "
            "Returns access & refresh JWT tokens on success."
        ),
        request_body=SignInSerializer,
        responses={
            200: openapi.Response(
                description="OK – returns JWT tokens", schema=AuthResponseSerializer
            ),
            401: "Invalid credentials",
        },
    )
    def post(self, request):
        tokens = _facade.sign_in(request.data, context={"request": request})
        return Response(tokens)
