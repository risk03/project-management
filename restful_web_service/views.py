# Create your views here.
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import restful_web_service.models as models
import restful_web_service.serializers as serializers


class PositionView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            structure = models.Position.objects.all()
        else:
            structure = models.Position.objects.filter(id=pk)
        serializer = serializers.PositionSerializer(structure, many=True)
        return Response({"positions": serializer.data})

    def post(self, request, pk=None):
        position = request.data.get('positions')
        serializer = serializers.PositionSerializer(data=position)
        if serializer.is_valid(raise_exception=True):
            position = serializer.save()
        return Response({"success": "Position '{}' created successfully".format(position.name)})

    def put(self, request, pk):
        position = get_object_or_404(models.Position.objects.all(), pk=pk)
        data = request.data.get('positions')
        serializer = serializers.PositionSerializer(instance=position, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            article_saved = serializer.save()
            return Response({
                "success": "Position '{}' updated successfully".format(article_saved.name)
            })

    def delete(self, request, pk):
        position = get_object_or_404(models.Position.objects.all(), pk=pk)
        position.delete()
        return Response({
            "message": "Position with id `{}` has been deleted.".format(pk)
        }, status=204)


class ProjectView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            projects = models.TaskGroup.objects.filter(parent=None)
        else:
            projects = models.TaskComponent.objects.filter(id=pk)
        serializer = serializers.TaskComponentSerializer(projects,many=True)
        return Response({"projects": serializer.data})

    def post(self, request, pk=None):
        position = request.data.get('projects')
        isgroup = request.data.get('isgroup')
        if isgroup:
            serializer = serializers.TaskGroupSerializer(data=position)
        else:
            serializer = serializers.TaskLeafSerializer(data=position)
        if serializer.is_valid(raise_exception=True):
            position = serializer.save()
        return Response({"success": "Project '{}' created successfully".format(position.name)})