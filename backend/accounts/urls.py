from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationAPIView,
    login_view,
    logout_view,
    user_profile_view,
    user_profile_update_view,
)

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', user_profile_view, name='user-profile'),
    path('profile/update/', user_profile_update_view, name='user-profile-update'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]

