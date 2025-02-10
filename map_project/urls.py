from django.contrib import admin
from django.urls import path, include  # include is needed to add app urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('map_app.urls')),  # Include the map_app URLs
    # path('', include('map_app.urls')),  # Include the map_app API
    
]
