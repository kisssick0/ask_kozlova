from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index),
    path('tag', views.tag),
    path('question', views.question),
    path('login', views.login),
    path('register', views.register),
    path('ask', views.ask),
    path('settings', views.settings)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)