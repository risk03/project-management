from rest_framework import serializers

from restful_web_service.models import Position, TaskGroup, TaskLeaf, TaskComponent


class PostionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'


class TaskComponentSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        if hasattr(instance, 'taskgroup'):
            return TaskGroupSerializer(instance=instance.taskgroup).data
        elif hasattr(instance, 'taskleaf'):
            return TaskLeafSerializer(instance=instance.taskleaf).data
        else:
            print(1)
    class Meta:
        model = TaskComponent
        fields='__all__'

class TaskGroupSerializer(serializers.ModelSerializer):
    child = TaskComponentSerializer(many=True)
    class Meta:
        model = TaskGroup
        fields = '__all__'
        depth = 2

class TaskLeafSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLeaf
        fields = '__all__'
        depth = 2