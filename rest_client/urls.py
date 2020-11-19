from django.urls import path
from . import views
urlpatterns = [
    path('positions/', views.position, name='positions'),
    path('positions/<int:pk>', views.position, name='positions'),
    path('tasks/', views.projects, name='tasks'),
    path('tasks/<int:pk>', views.projects, name='tasks'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout')
]