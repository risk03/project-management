from django.urls import path

import restful_web_service.views as views

app_name = "restful_web_service"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('positions/', views.PositionView.as_view()),
    path('positions/<int:pk>/', views.PositionView.as_view()),
    path('projects/', views.ProjectView.as_view()),
    path('projects/<int:pk>/', views.ProjectView.as_view()),
]
