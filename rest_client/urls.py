from django.urls import path
from .views import position
urlpatterns = [
    path('position/', position, name='position'),
]