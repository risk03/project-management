from django.urls import path

import restful_web_service.views as views

app_name = "restful_web_service"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('positions/', views.PositionView.as_view()),
    path('positions/<int:pk>/', views.PositionView.as_view()),
    path('tasks/', views.TaskView.as_view()),
    path('tasks/of/struct/<int:pk>', views.TaskOfStructView.as_view()),
    path('tasks/of/sys/<int:pk>', views.TaskOfSysView.as_view()),
    path('taskgroups/', views.TaskGroupView.as_view()),
    path('tasks/<int:pk>/', views.TaskView.as_view()),
    path('systems/', views.SystemView.as_view()),
    path('systemparts/', views.SystempartsView.as_view()),
    path('systemgroups/', views.SystemGroupView.as_view()),
    path('systems/<int:pk>/', views.SystemView.as_view()),
    path('structures/', views.StructureView.as_view()),
    path('structures/<int:pk>/', views.StructureView.as_view()),
    path('divisions/', views.DivisionView.as_view()),
    path('artefacts/', views.ArtefactView.as_view()),
    path('artefacts/<int:pk>/', views.ArtefactView.as_view()),
    path('sequences/', views.TaskSequenceView.as_view()),
    path('sequences/<int:pk>/', views.TaskSequenceView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('employees/', views.EmployeeView.as_view())
]
