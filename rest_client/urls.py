from django.urls import path
from .views import vote
urlpatterns = [
    path('structure/', vote, name='vote'),
]