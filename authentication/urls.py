# from django.urls import path
# from rest_framework_simplejwt.views import TokenRefreshView
# from .views import (
#     CustomTokenObtainPairView,
#     register,
#     login,
#     logout,
#     UserListCreateView,
# )

# urlpatterns = [
#     # JWT Token endpoints
#     path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
#     path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

#     # Authentication endpoints
#     path("login/", login, name="login"),
#     path("register/", register, name="register"),
#     path("logout/", logout, name="logout"),
    
#     # User management
#     path("users/", UserListCreateView.as_view(), name="user_list_create"),
# ]

from django.urls import path
from .views import (
    simple_login,
    simple_logout,
    get_current_user,
    UserListCreateView,
)

urlpatterns = [
    path("login/", simple_login, name="simple_login"),
    path("logout/", simple_logout, name="simple_logout"),
    path("user/", get_current_user, name="current_user"),
    
    # Keep user management for admin
    path("users/", UserListCreateView.as_view(), name="user_list_create"),
]