from rest_framework import serializers

from restful_web_service.models import Division, Employee, StructureComponent

class StructureComponentSerializer(serializers.ModelSerializer):
    pass
class EmployeeSerializer(StructureComponentSerializer):
    pass
class DivisionSerializer(StructureComponentSerializer):
    pass

class StructureComponentSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(many=True, read_only=True)
    division = DivisionSerializer(many=True, read_only=True)
    fields = ['employee', 'division']

class EmployeeSerializer(StructureComponentSerializer):
    class Meta:
        model = Employee
        fields = ['full_name', 'position', 'short_name']

class DivisionSerializer(StructureComponentSerializer):
    subdivisions = StructureComponentSerializer(many=True, read_only=True)

    class Meta:
        model = Division
        fields = ['name', 'subdivisions']