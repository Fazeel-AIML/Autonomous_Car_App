from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='map_view'),
    path('api/gps-data/', views.gps_data, name='gps_data'), # This is the API endpoint
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('video_feed/', views.stream_view, name='video_feed'),

]