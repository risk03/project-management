# Create your views here.
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import restful_web_service.models as models
import restful_web_service.serializers as serializers


class PositionView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        structures = models.Position.objects.all()
        serializer = serializers.PostionSerializer(structures, many=True)
        return Response({"positions": serializer.data})

    def post(self, request):
        structures = models.Position.objects.all()
        serializer = serializers.PostionSerializer(structures, many=True)
        return Response({"positions": serializer.data})


class ProjectView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        projects = models.TaskGroup.objects.filter(parent=None)
        serializer = serializers.TaskGroupSerializer(projects, many=True)
        return Response({"projects": serializer.data})