from django.urls import path
from .views import PositionView
app_name = "restful_web_service"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('position/', PositionView.as_view()),
]
