# Create your views here.
import hashlib

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import restful_web_service.models as models
import restful_web_service.serializers as serializers


class LoginView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = models.Employee.objects.filter(login=request.data['login']).first()
        if not user:
            return Response({'status': 'failed'})
        if hashlib.md5((request.data['password'] + user.salt).encode('utf-8')).hexdigest() == user.hash:
                return Response({'status': 'success', 'id': user.id})
        else:
            return Response({'status': 'failed'})


# noinspection PyMethodMayBeStatic
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
            saved = serializer.save()
            return Response({
                "success": "Position '{}' updated successfully".format(saved.name)
            })

    def delete(self, request, pk):
        position = get_object_or_404(models.Position.objects.all(), pk=pk)
        position.delete()
        return Response({
            "message": "Position with id `{}` has been deleted.".format(pk)
        }, status=204)


# noinspection PyMethodMayBeStatic
class TaskView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            tasks = models.TaskGroup.objects.filter(parent=None)
        else:
            tasks = models.TaskComponent.objects.filter(id=pk)
        serializer = serializers.TaskComponentSerializer(tasks, many=True)
        return Response({"tasks": serializer.data})

    def post(self, request, pk=None):
        tasks = request.data.get('tasks')
        isgroup = request.data.get('isgroup')
        if isgroup:
            serializer = serializers.TaskGroupSerializer(data=tasks)
        else:
            serializer = serializers.TaskLeafSerializer(data=tasks)
        if serializer.is_valid(raise_exception=True):
            tasks = serializer.save()
        return Response({"success": "Task '{}' created successfully".format(tasks.name)})

    def put(self, request, pk):
        isgroup = request.data.get("isgroup")
        data = request.data.get('tasks')
        if isgroup:
            tasks = get_object_or_404(models.TaskGroup.objects.all(), pk=pk)
            serializer = serializers.TaskGroupSerializer(instance=tasks, data=data, partial=True)
        else:
            tasks = get_object_or_404(models.TaskLeaf.objects.all(), pk=pk)
            serializer = serializers.TaskLeafSerializer(instance=tasks, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            saved = serializer.save()
            return Response({
                "success": "Task '{}' updated successfully".format(saved.name)
            })

    def delete(self, request, pk):
        tasks = get_object_or_404(models.TaskComponent.objects.all(), pk=pk)
        tasks.delete()
        return Response({
            "message": "Task with id `{}` has been deleted.".format(pk)
        }, status=204)


# noinspection PyMethodMayBeStatic
class TaskSequenceView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            sequences = models.TaskSequence.objects.all()
        else:
            sequences = models.TaskSequence.objects.filter(id=pk)
        serializer = serializers.TaskSequenceSerializer(sequences, many=True)
        return Response({"sequences": serializer.data})

    def post(self, request, pk=None):
        sequences = request.data.get('sequences')
        serializer = serializers.TaskSequenceSerializer(data=sequences)
        if serializer.is_valid(raise_exception=True):
            sequences = serializer.save()
        return Response({"success": "Sequence '{}' created successfully".format(sequences.name)})

    def put(self, request, pk):
        sequences = get_object_or_404(models.TaskSequence.objects.all(), pk=pk)
        data = request.data.get('sequences')
        serializer = serializers.TaskSequenceSerializer(instance=sequences, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            saved = serializer.save()
            return Response({
                "success": "Sequence '{}' updated successfully".format(saved.name)
            })

    def delete(self, request, pk):
        sequences = get_object_or_404(models.TaskSequence.objects.all(), pk=pk)
        sequences.delete()
        return Response({
            "message": "Sequence with id `{}` has been deleted.".format(pk)
        }, status=204)


# noinspection PyMethodMayBeStatic
class StructureView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            tasks = models.StructureComponent.objects.filter(parent=None)
        else:
            tasks = models.StructureComponent.objects.filter(id=pk)
        serializer = serializers.StructureComponentSerializer(tasks, many=True)
        return Response({"structures": serializer.data})

    def post(self, request, pk=None):
        structures = request.data.get('structures')
        isgroup = request.data.get('isgroup')
        if isgroup:
            serializer = serializers.DivisionSerializer(data=structures)
        else:
            serializer = serializers.EmployeeSerializer(data=structures)
        if serializer.is_valid(raise_exception=True):
            structures = serializer.save()
        return Response({"success": "Structure '{}' created successfully".format(structures.name)})

    def put(self, request, pk):
        isgroup = request.data.get("isgroup")
        data = request.data.get('structures')
        if isgroup:
            structures = get_object_or_404(models.Division.objects.all(), pk=pk)
            serializer = serializers.DivisionSerializer(instance=structures, data=data, partial=True)
        else:
            structures = get_object_or_404(models.Employee.objects.all(), pk=pk)
            serializer = serializers.EmployeeSerializer(instance=structures, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            saved = serializer.save()
            return Response({
                "success": "Employee '{}' updated successfully".format(saved.name)
            })

    def delete(self, request, pk):
        tasks = get_object_or_404(models.StructureComponent.objects.all(), pk=pk)
        tasks.delete()
        return Response({
            "message": "Structure with id `{}` has been deleted.".format(pk)
        }, status=204)


# noinspection PyMethodMayBeStatic
class ArtefactView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            artefact = models.Artefact.objects.all()
        else:
            artefact = models.Artefact.objects.filter(id=pk)
        serializer = serializers.ArtefactSerializer(artefact, many=True)
        return Response({"artefacts": serializer.data})

    def post(self, request, pk=None):
        artefacts = request.data.get('artefacts')
        serializer = serializers.ArtefactSerializer(data=artefacts)
        if serializer.is_valid(raise_exception=True):
            artefacts = serializer.save()
        return Response({"success": "Artefact '{}' created successfully".format(artefacts.name)})

    def put(self, request, pk):
        artefacts = get_object_or_404(models.Artefact.objects.all(), pk=pk)
        data = request.data.get('artefacts')
        serializer = serializers.ArtefactSerializer(instance=artefacts, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            saved = serializer.save()
            return Response({
                "success": "Artefact '{}' updated successfully".format(saved.name)
            })

    def delete(self, request, pk):
        artefacts = get_object_or_404(models.Artefact.objects.all(), pk=pk)
        artefacts.delete()
        return Response({
            "message": "Artefact with id `{}` has been deleted.".format(pk)
        }, status=204)


# noinspection PyMethodMayBeStatic
class SystemView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            systems = models.SystemComponent.objects.filter(parent=None)
        else:
            systems = models.SystemComponent.objects.filter(id=pk)
        serializer = serializers.SystemComponentSerializer(systems, many=True)
        return Response({"systems": serializer.data})

    def post(self, request, pk=None):
        systems = request.data.get('systems')
        isgroup = request.data.get('isgroup')
        if isgroup:
            serializer = serializers.SystemGroupSerializer(data=systems)
        else:
            serializer = serializers.SystemPartSerializer(data=systems)
        if serializer.is_valid(raise_exception=True):
            systems = serializer.save()
        return Response({"success": "System '{}' created successfully".format(systems.name)})

    def put(self, request, pk):
        isgroup = request.data.get("isgroup")
        data = request.data.get('systems')
        if isgroup:
            systems = get_object_or_404(models.SystemGroup.objects.all(), pk=pk)
            serializer = serializers.SystemGroupSerializer(instance=systems, data=data, partial=True)
        else:
            systems = get_object_or_404(models.SystemPart.objects.all(), pk=pk)
            serializer = serializers.SystemPartSerializer(instance=systems, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            saved = serializer.save()
            return Response({
                "success": "System '{}' updated successfully".format(saved.name)
            })

    def delete(self, request, pk):
        tasks = get_object_or_404(models.SystemComponent.objects.all(), pk=pk)
        tasks.delete()
        return Response({
            "message": "System with id `{}` has been deleted.".format(pk)
        }, status=204)
