from django.urls import path
from . import views

urlpatterns = [
    path('company_details/', views.get_about)
]