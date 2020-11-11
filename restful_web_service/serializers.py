from rest_framework import serializers

import restful_web_service.models as models


class TaskComponentSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        if hasattr(instance, 'taskgroup'):
            return TaskGroupSerializer(instance=instance.taskgroup).data
        elif hasattr(instance, 'taskleaf'):
            return TaskLeafSerializer(instance=instance.taskleaf).data
        else:
            print(1)

    class Meta:
        model = models.TaskComponent
        fields = '__all__'


class TaskLeafSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TaskLeaf
        fields = '__all__'


class ArtefactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artefact
        fields = '__all__'


class TaskGroupSerializer(serializers.ModelSerializer):
    child = TaskComponentSerializer(many=True, read_only=True)

    class Meta:
        model = models.TaskGroup
        fields = '__all__'


class TaskSequenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TaskSequence
        fields = '__all__'


class StructureComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StructureComponent
        fields = '__all__'


class DivisionSerializer(serializers.ModelSerializer):
    child = StructureComponentSerializer(many=True, read_only=True)
    class Meta:
        model = models.Division
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Employee
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Position
        fields = '__all__'


class SystemComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SystemComponent
        fields = '__all__'


class SystemGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SystemGroup
        fields = '__all__'


class SystemPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SystemPart
        fields = '__all__'
