from .views import soap_bank_app
from django.urls import path
urlpatterns = [
    path('', soap_bank_app),
]
