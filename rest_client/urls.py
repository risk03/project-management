from django.urls import path
from . import views
urlpatterns = [
    path('position/', views.position, name='position'),
    path('login/', views.login, name='login')
]