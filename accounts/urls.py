from django.urls import path
from .views import SignupView, LoginView, LogoutView, RefreshTokenView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='token_blacklist'),
    path('refresh/', RefreshTokenView.as_view(), name='token_refresh'),
]
