from datetime import datetime

from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import SignInSerializer, SignUpSerializer


class JWTService:
    """Wrapper on top of SimpleJWT tokens with custom lifetime support."""

    @staticmethod
    def generate_tokens(user):
        # Create refresh & access tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Override access-token expiration if configured
        token_lifetime = getattr(settings, "SIMPLE_JWT", {}).get(
            "ACCESS_TOKEN_LIFETIME"
        )
        if token_lifetime:
            # compute new expiry timestamp
            exp = datetime.utcnow() + token_lifetime
            access.payload["exp"] = int(exp.timestamp())

        # Calculate expires_in as seconds until expiration
        expires_in = access.payload["exp"] - int(datetime.utcnow().timestamp())

        return {
            "access": str(access),
            "refresh": str(refresh),
            "token_type": "Bearer",
            "expires_in": int(expires_in),
        }

    @staticmethod
    def validate_token(token: str):
        from rest_framework_simplejwt.authentication import JWTAuthentication

        try:
            JWTAuthentication().get_validated_token(token)
            return True
        except Exception:
            return False


class AuthenticationFacadeService:
    """High‑level API so callers deal only with signup/signin DTOs."""

    signup_serializer_class = SignUpSerializer
    signin_serializer_class = SignInSerializer

    def sign_up(self, data, context=None):
        serializer = self.signup_serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return JWTService.generate_tokens(user)

    def sign_in(self, data, context=None):
        serializer = self.signin_serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return JWTService.generate_tokens(user)
