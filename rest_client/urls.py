from django.urls import path
from . import views
urlpatterns = [
    path('positions/', views.position, name='positions'),
    path('positions/<int:pk>', views.position, name='positions'),
    path('tasks/', views.projects, name='projects'),
    path('tasks/<int:pk>', views.tasks, name='tasks'),
    path('tasks/add_group/', views.add_tasks_group, name='task_add_group'),
    path('tasks/add_group/<int:pk>', views.add_tasks_group, name='task_add_group'),
    path('structures/', views.structures_root, name='structures_root'),
    path('structures/<int:pk>', views.structures, name='structures'),
    path('structures/add_group/', views.add_structure, name='add_structures'),
    path('structures/add_group/<int:pk>', views.add_employee, name='add_employee'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout')
]