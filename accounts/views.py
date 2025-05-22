from django.forms import ValidationError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.services import AuthenticationFacadeService
from docs.swagger.accounts.signin import USER_LOGIN_SCHEMA
from docs.swagger.accounts.signup import SIMPLE_LOGIN_VIEW_SCHEMA

_facade = AuthenticationFacadeService()


class SignUpView(APIView):
    """
    post:
    Register a new user with a username and password, returning JWT tokens.
    """

    permission_classes = []

    @swagger_auto_schema(**SIMPLE_LOGIN_VIEW_SCHEMA)
    def post(self, request):
        tokens = _facade.sign_up(request.data, context={"request": request})
        return Response(tokens, status=status.HTTP_201_CREATED)


class SignInView(APIView):
    """
    post:
    Authenticate a user and return JWT tokens.
    """

    permission_classes = []

    @swagger_auto_schema(**USER_LOGIN_SCHEMA)
    def post(self, request):
        try:
            tokens = _facade.sign_in(request.data, context={"request": request})
            return Response(tokens, status=status.HTTP_200_OK)
        except ValidationError as exc:
            return Response(
                {"authorization": exc.detail}, status=status.HTTP_401_UNAUTHORIZED
            )
        except:
            return Response(
                {"authorization": "error"}, status=status.HTTP_401_UNAUTHORIZED
            )
