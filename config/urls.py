from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)


urlpatterns = [
    # Default
    path('admin/', admin.site.urls),

    # Third party
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/login/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Local
    path('api/', include('quotes_interface.urls')),
    path('api/', include('authentication.urls')),
    path('api/', include('race_handler.urls'))
]
