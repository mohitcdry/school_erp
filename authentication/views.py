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
from rest_framework.permissions import AllowAny, IsAuthenticated
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

    print("=== DEBUG LOGIN ===")
    print(f"Request data: {request.data}")
    print(f"Request content type: {request.content_type}")

    serializer = SimpleLoginSerializer(data=request.data)
    if serializer.is_valid():
        username_or_email = serializer.validated_data["username_or_email"]
        password = serializer.validated_data["password"]
        print(f"Input - Username/Email: {username_or_email}")
        print(f"Input - Password: {password}")

        # Try to find user by username first, then email
        authenticated_user = None
        try:
            if '@' in username_or_email:
                # It's an email - finds user by email
                print("Trying to find user by email...")
                user_obj = User.objects.get(email=username_or_email)
                print(f"Found user: {user_obj.username}")
                print(f"User is active: {user_obj.is_active}")
                print(f"Password check: {user_obj.check_password(password)}")

                authenticated_user = authenticate(request, username=username_or_email, password=password)
                print(f"Authenticate result: {authenticated_user}")
        
            else:
                # It's a username
                print("Trying to find user by username...")
                user_obj = authenticate(request, username=username_or_email, password=password)
                print(f"Found user: {user_obj.username}")
                print(f"User is active: {user_obj.is_active}")
                print(f"Password check: {user_obj.check_password(password)}")

                authenticated_user = authenticate(request, username=username_or_email, password=password)
                print(f"Authenticate result: {authenticated_user}")
                
        except User.DoesNotExist:
            print("User does not exist")
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if authenticated_user and authenticated_user.is_active:
            login(request, authenticated_user)  
            return Response({
                    "message": "Login successful",
                    "user":{
                    # UserSerializer(user).data,
                    "id": authenticated_user.id,
                    "username": authenticated_user.username,
                    "email": authenticated_user.email,
                    "role": authenticated_user.role,
                    "first_name": authenticated_user.first_name,
                    "last_name": authenticated_user.last_name,
                }      
            })
        else:
            print("Authentication failed or user inactive")
            return Response(
                {"error": "Invalid credentials or account disabled"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    else:
        print(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current authenticated user"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_exempt 
def simple_logout(request):
    """Simple logout using Django session"""
    if request.user.is_authenticated:
        logout(request)
        return Response({"message": "Logged out successfully"})
    else:
        return Response({"message": "Already logged out"})
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
