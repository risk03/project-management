from django.db.models import QuerySet
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Division, Employee, StructureComponent, Position
from .serializers import PostionSerializer

class OrganizationStructure(APIView):
    def get(self, request):
        structures = Position.objects.all()
        serializer = PostionSerializer(structures, many=True)
        return Response({"positions": serializer.data})