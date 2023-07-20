from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static


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
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Local
    path('api/', include('quotes_interface.urls')),
    path('api/', include('authentication.urls')),
    path('api/', include('race_handler.urls')),
    path('api/', include('statistics_page.urls')),
    re_path(r'^.*/$', TemplateView.as_view(template_name="index.html")),
    re_path(r'^', TemplateView.as_view(template_name="index.html")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
