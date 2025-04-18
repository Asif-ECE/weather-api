from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers

from django.contrib.auth import get_user_model
from .serializers import SignupSerializer, LoginSerializer, LogoutSerializer


User = get_user_model()

@extend_schema(
    summary="User Signup",
    description="Creates a new user account and returns JWT access and refresh tokens.",
    tags=["Authentication"],
    request=SignupSerializer,
    responses={
        201: inline_serializer(
            name="SignupResponse",
            fields={
                "message": serializers.CharField(),
                "access": serializers.CharField(),
                "refresh": serializers.CharField()
            }
        ),
        400: OpenApiResponse(description="Validation error")
    }
)
class SignupView(CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(username=response.data['username'])
        refresh = RefreshToken.for_user(user)
        response.data = {
            "message": "Signup successful.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
        return response


@extend_schema(
    summary="User Login",
    description="Authenticates a user and returns a new pair of access and refresh tokens.",
    tags=["Authentication"],
    request=LoginSerializer,
    responses={
        200: inline_serializer(
            name="LoginResponse",
            fields={
                "access": serializers.CharField(),
                "refresh": serializers.CharField()
            }
        ),
        400: OpenApiResponse(description="Invalid login credentials")
    }
)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@extend_schema(
    summary="User Logout",
    description="Logs out a user by blacklisting the refresh token.",
    tags=["Authentication"],
    request=LogoutSerializer,
    responses={
        204: OpenApiResponse(description="Logout successful"),
        400: OpenApiResponse(description="Invalid or expired token")
    }
)
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Logout successful."}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    summary="Refresh JWT Token",
    description="Takes a valid refresh token and returns a new access token.",
    tags=["Authentication"]
)
class RefreshTokenView(TokenRefreshView):
    """
    Using standard view provided by `simplejwt` for refreshing tokens.
    """
    pass
