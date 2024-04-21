from django.urls import path
from .views import RegisterView, LogoutView

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='auth_signup'),
    path('logout/', LogoutView.as_view(), name='auth_logout')
]
