from django.urls import path
from . import views
urlpatterns = [
    path('positions/', views.position, name='positions'),
    path('positions/<int:pk>', views.position, name='positions'),
    path('tasks/', views.projects, name='projects'),
    path('tasks/<int:pk>', views.tasks, name='tasks'),
    path('tasks/add/', views.add_project, name='task_add'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout')
]