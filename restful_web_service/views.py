from django.db.models import QuerySet
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Division, Employee, StructureComponent
from .serializers import DivisionSerializer, EmployeeSerializer

class OrganizationStructure(APIView):
    def get(self, request):
        structures = StructureComponent.objects.all()
        for i in structures:
            print(i)
        serializer = EmployeeSerializer(structures)
        r = serializer.data
        return Response({"structure": serializer.data})