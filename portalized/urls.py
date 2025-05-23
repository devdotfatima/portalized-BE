"""
URL configuration for portalized project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from .swagger import schema_view 


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("authentication.urls")),
    path("users/", include("users.urls")),
    path("products/", include("products.urls")),
    path("orders/", include("orders.urls")),
    path("cart/", include("cart.urls")),
    path("podcasts", include("podcasts.urls")),
    path("reviews/", include("productreviews.urls")),
    path("contact-us",include("contactus.urls")),
    path("sports",include("sports.urls")),
    path('posts/', include('posts.urls')),
    path('coachingsessions',include('coachingsessions.urls')),
    path("",include('chat.urls')),
    path("notifications",include('notifications.urls')),
    path("relationships/",include('relationships.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
     path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
]
