from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.services import AuthenticationFacadeService

_facade = AuthenticationFacadeService()


class SignUpView(APIView):
    permission_classes = []

    def post(self, request):
        tokens = _facade.sign_up(request.data, context={"request": request})
        return Response(tokens, status=status.HTTP_201_CREATED)


class SignInView(APIView):
    permission_classes = []

    def post(self, request):
        tokens = _facade.sign_in(request.data, context={"request": request})
        return Response(tokens)
