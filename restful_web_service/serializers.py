from rest_framework import serializers

from restful_web_service.models import Division, Employee, StructureComponent, Position

class PostionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ["id", "name"]