from rest_framework import viewsets

from clinic.models import AppointmentSlot, Doctor
from clinic.permissions import IsAdminOrReadOnly
from clinic.serializers import AppointmentSlotSerializer, DoctorSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAdminOrReadOnly]


class AppointmentSlotViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSlotSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = AppointmentSlot.objects.select_related("doctor").all()

        doctor = self.request.query_params.get("doctor")
        date = self.request.query_params.get("date")
        is_available = self.request.query_params.get("is_available")

        if doctor:
            queryset = queryset.filter(doctor_id=doctor)

        if date:
            queryset = queryset.filter(date=date)

        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == "true")

        return queryset
