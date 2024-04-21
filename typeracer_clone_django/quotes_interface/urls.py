from django.urls import path

from .views import quote_generator


urlpatterns = [
    path('generate_quote/', quote_generator, name='quote_generator')
]
