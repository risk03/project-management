from rest_framework import serializers

from restful_web_service.models import Division, Employee, StructureComponent, Position, TaskGroup

class PostionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ["id", "name"]


class TaskGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskGroup
        fields=["id", "parent", 'name', 'creator', 'responsible', 'child']
