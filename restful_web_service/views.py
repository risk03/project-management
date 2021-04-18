# Create your views here.
import hashlib

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import restful_web_service.models as models
import restful_web_service.serializers as serializers


# noinspection PyMethodMayBeStatic
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

    # noinspection PyUnusedLocal
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
class TaskOfStructView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        tasks = models.TaskLeaf.objects.filter(responsible=pk)
        serializer = serializers.TaskComponentSerializer(tasks, many=True)
        return Response({"tasks": serializer.data})  # noinspection PyMethodMayBeStatic


# noinspection PyMethodMayBeStatic
class TaskOfSysView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        tasks = models.TaskLeaf.objects.filter(system=pk)
        serializer = serializers.TaskComponentSerializer(tasks, many=True)
        return Response({"tasks": serializer.data})


class ProjectLeaves(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def deeper(o, out_list):
        for task in o.child.all():
            if hasattr(task, 'taskgroup'):
                ProjectLeaves.deeper(task.taskgroup, out_list)
            else:
                out_list.append(task.taskleaf)

    def get(self, request, pk):
        project = models.TaskGroup.objects.filter(pk=pk)[0]
        tasks = []
        ProjectLeaves.deeper(project, tasks)
        serializer = serializers.TaskLeafSerializer(tasks, many=True)
        return Response({"tasks": serializer.data})


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

    # noinspection PyUnusedLocal
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
        return Response({"message": "Task with id `{}` has been deleted.".format(pk)}, status=204)


# noinspection PyMethodMayBeStatic
class StructureView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            tasks = models.Division.objects.filter(parent=None)
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
            serializer.save()
        return Response({"success": "Structure '{}' created successfully".format(pk)})

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
            serializer.save()
            return Response({"success": "Structure '{}' updated successfully".format(pk)})

    def delete(self, request, pk):
        tasks = get_object_or_404(models.StructureComponent.objects.all(), pk=pk)
        deldiv(tasks)
        return Response({
            "message": "Structure with id `{}` has been deleted.".format(pk)
        }, status=204)


# noinspection PyUnresolvedReferences
def deldiv(division):
    if hasattr(division, 'division'):
        subs = division.division.child.all()
        for sub in subs:
            deldiv(sub)
        division.delete()


# noinspection PyMethodMayBeStatic
class DivisionView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = models.Division.objects.all()
        serializer = serializers.StructureComponentSerializer(tasks, many=True)
        return Response({"divisions": serializer.data})


# noinspection PyMethodMayBeStatic
class EmployeeView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            employees = models.Employee.objects.all()
        else:
            employees = models.Employee.objects.filter(id=pk)
        serializer = serializers.EmployeeSerializer(employees, many=True)
        return Response({"employees": serializer.data})


# noinspection PyMethodMayBeStatic
class ArtefactOfView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        artefact = models.Artefact.objects.filter(task=pk)
        serializer = serializers.ArtefactSerializer(artefact, many=True)
        return Response({"artefacts": serializer.data})


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

    # noinspection PyUnusedLocal
    def post(self, request, pk=None):
        artefacts = request.data.get('artefacts')
        serializer = serializers.ArtefactSerializer(data=artefacts)
        if serializer.is_valid(raise_exception=True):
            artefacts = serializer.save()
        return Response({"success": "Artefact '{}' created successfully".format(artefacts.title)})

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
class SystempartsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        systems = models.SystemComponent.objects.all()
        serializer = serializers.SystemComponentSerializer(systems, many=True)
        return Response({"systemparts": serializer.data})


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

    # noinspection PyUnusedLocal
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


# noinspection PyMethodMayBeStatic
class SystemGroupView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        systems = models.SystemGroup.objects.all()
        serializer = serializers.SystemComponentSerializer(systems, many=True)
        return Response({"systemgroups": serializer.data})


# noinspection PyMethodMayBeStatic
class TaskGroupView(APIView):
    def get(self, request):
        groups = models.TaskGroup.objects.all()
        serializer = serializers.TaskComponentSerializer(groups, many=True)
        return Response({"taskgroups": serializer.data})


# noinspection PyMethodMayBeStatic
class PertView(APIView):
    def get(self, request, pk=None):
        if pk is None:
            return Response({"error": "no pk"})
        else:
            task_group = models.TaskGroup.objects.get(id=pk)
            task_group.get_time()
            return Response({"ok": "ok!"})
