# Create your views here.
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Position
from .serializers import PostionSerializer


class OrganizationStructure(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        structures = Position.objects.all()
        serializer = PostionSerializer(structures, many=True)
        return Response({"positions": serializer.data})
