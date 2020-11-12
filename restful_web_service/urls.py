from django.urls import path

import restful_web_service.views as views

app_name = "restful_web_service"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('positions/', views.PositionView.as_view()),
    path('positions/<int:pk>/', views.PositionView.as_view()),
    path('tasks/', views.TaskView.as_view()),
    path('tasks/<int:pk>/', views.TaskView.as_view()),
    path('systems/', views.SystemView.as_view()),
    path('systems/<int:pk>/', views.SystemView.as_view()),
    path('structures/', views.StructureView.as_view()),
    path('structures/<int:pk>/', views.StructureView.as_view()),
    path('artefacts/', views.ArtefactView.as_view()),
    path('artefacts/<int:pk>/', views.ArtefactView.as_view()),
    path('sequences/', views.TaskSequenceView.as_view()),
    path('sequences/<int:pk>/', views.TaskSequenceView.as_view()),
]
