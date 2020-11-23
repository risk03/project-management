from django.urls import path
from . import views
urlpatterns = [
    path('positions/', views.positions_root, name='position'),
    path('positions/<int:pk>', views.positions, name='positions'),
    path('tasks/', views.projects, name='projects'),
    path('tasks/<int:pk>', views.tasks, name='tasks'),
    path('tasks/add_group/', views.add_tasks_group, name='task_add_group'),
    path('tasks/add_group/<int:pk>', views.add_tasks_group, name='task_add_group'),
    path('structures/', views.structures_root, name='structures_root'),
    path('structures/<int:pk>', views.structures, name='structures'),
    path('structures/add_group/', views.add_structure, name='add_structures'),
    path('structures/add_group/<int:pk>', views.add_structure, name='add_structures'),
    path('systems/', views.systems_root, name='systems_root'),
    path('systems/<int:pk>', views.systems, name='systems'),
    path('systems/add_group/', views.add_system, name='add_system'),
    path('systems/add_group/<int:pk>', views.add_system, name='add_system'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout')
]