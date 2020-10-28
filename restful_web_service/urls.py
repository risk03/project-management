from django.urls import path
from .views import OrganizationStructure
app_name = "restful_web_service"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('structure/', OrganizationStructure.as_view()),
]
