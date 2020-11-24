from django.urls import path
from . import views
urlpatterns = [
    path('positions/', views.positions_root, name='position_root'),
    path('employees/', views.employees_root, name='employees_root'),
    path('positions/add/', views.positions_add, name='position_add'),
    path('positions/<int:pk>', views.positions, name='positions'),
    path('tasks/', views.projects, name='projects'),
    path('tasks/<int:pk>', views.tasks, name='tasks'),
    path('tasks/add_group/', views.add_tasks_group, name='task_add_group'),
    path('tasks/add_group/<int:pk>', views.add_tasks_group, name='task_add_group'),
    path('structures/', views.structures_root, name='structures_root'),
    path('structures/<int:pk>', views.structures, name='structures'),
    path('structures/reset_password/<int:pk>', views.reset_password, name='reset_password'),
    path('structures/add_group/', views.add_structure, name='add_structure'),
    path('structures/add_group/<int:pk>', views.add_structure, name='add_structure'),
    path('structures/add_leaf/<int:pk>', views.add_structure_leaf, name='add_structure_leaf'),
    path('systems/', views.systems_root, name='systems_root'),
    path('systems/<int:pk>', views.systems, name='systems'),
    path('systems/add_group/', views.add_system_group, name='add_system'),
    path('systems/add_group/<int:pk>', views.add_system_group, name='add_system'),
    path('systems/add_leaf/<int:pk>', views.add_system_leaf, name='add_system_leaf'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout')
]