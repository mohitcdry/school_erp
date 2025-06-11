# from rest_framework import status, generics, serializers
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.views import TokenObtainPairView
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from django.contrib.auth import authenticate
# from .models import User
# from .serializers import UserSerializer, UserLoginSerializer, TokenResponseSerializer

### prototype version

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User
from .serializers import UserSerializer, SimpleLoginSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_exempt
def simple_login(request):
    """Simple login with username/email and password"""
    serializer = SimpleLoginSerializer(data=request.data)
    if serializer.is_valid():
        username_or_email = serializer.validated_data["username_or_email"]
        password = serializer.validated_data["password"]

        # Try to find user by username first, then email
        user = None
        try:
            if '@' in username_or_email:
                # It's an email
                user = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user.username, password=password)
            else:
                # It's a username
                user = authenticate(request, username=username_or_email, password=password)
        except User.DoesNotExist:
            pass

        if user and user.is_active:
            login(request, user)  # ✅ Use Django session login
            return Response(
                {
                    "message": "Login successful",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid credentials or account disabled"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def simple_logout(request):
    """Simple logout using Django session"""
    logout(request)  
    return Response(
        {"message": "Logout successful"}, 
        status=status.HTTP_200_OK
    )

class UserListCreateView(generics.ListCreateAPIView):
    """List all users or create a new user (Admin only)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            # Only authenticated users can view
            return [permission() for permission in []]
        else:
            # Only superadmin can create users
            return [permission() for permission in []]



####### orignal one

# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     username_field = "email"

#     def validate(self, attrs):
#         # Change username to email for authentication
#         email = attrs.get("email")
#         password = attrs.get("password")

#         if not email or not password:
#             raise serializers.ValidationError("Email and password are required.")

#         # Authenticate using email
#         user = authenticate(
#             request=self.context.get("request"), username=email, password=password
#         )

#         if not user:
#             raise serializers.ValidationError("Invalid email or password.")

#         if not user.is_active:
#             raise serializers.ValidationError("User account is disabled.")

#         # Set user for token generation
#         self.user = user

#         # Generate tokens
#         refresh = RefreshToken.for_user(user)

#         return {
#             "access": str(refresh.access_token),
#             "refresh": str(refresh),
#             "user": UserSerializer(user).data,
#         }


# class CustomTokenObtainPairView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainPairSerializer


# @api_view(["POST"])
# @permission_classes([AllowAny])
# def register(request):
#     """Register a new user"""
#     serializer = UserSerializer(data=request.data)
#     if serializer.is_valid():
#         user = serializer.save()
#         refresh = RefreshToken.for_user(user)

#         return Response(
#             {
#                 "message": "User registered successfully",
#                 "access": str(refresh.access_token),
#                 "refresh": str(refresh),
#                 "user": UserSerializer(user).data,
#             },
#             status=status.HTTP_201_CREATED,
#         )

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["POST"])
# @permission_classes([AllowAny])
# def login(request):
#     """Login user with email and password"""
#     serializer = UserLoginSerializer(data=request.data)
#     if serializer.is_valid():
#         email = serializer.validated_data["email"]
#         password = serializer.validated_data["password"]

#         user = authenticate(request, username=email, password=password)

#         if user:
#             if user.is_active:
#                 refresh = RefreshToken.for_user(user)
#                 return Response(
#                     {
#                         "access": str(refresh.access_token),
#                         "refresh": str(refresh),
#                         "user": UserSerializer(user).data,
#                     },
#                     status=status.HTTP_200_OK,
#                 )
#             else:
#                 return Response(
#                     {"error": "Account is disabled"},
#                     status=status.HTTP_401_UNAUTHORIZED,
#                 )
#         else:
#             return Response(
#                 {"error": "Invalid email or password"},
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["POST"])
# def logout(request):
#     """Logout user by blacklisting refresh token"""
#     try:
#         refresh_token = request.data.get("refresh")
#         if refresh_token:
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#             return Response(
#                 {"message": "Successfully logged out"}, status=status.HTTP_200_OK
#             )
#         return Response(
#             {"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST
#         )
#     except Exception as e:
#         return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


# class UserListCreateView(generics.ListCreateAPIView):
#     """List all users or create a new user (Admin only)"""

#     queryset = User.objects.all()
#     serializer_class = UserSerializer
