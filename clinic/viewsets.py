from rest_framework import viewsets

from clinic.models import Doctor
from clinic.permissions import IsAdminOrReadOnly
from clinic.serializers import DoctorSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAdminOrReadOnly]
