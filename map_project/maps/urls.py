# maps/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('add/', views.add_location, name='add_location'),
    path('edit/<int:pk>/', views.edit_location, name='edit_location'),
    path('delete/<int:pk>/', views.delete_location, name='delete_location'),
    path('location/<int:pk>/', views.location_detail, name='location_detail')
]