from django.db import transaction
from rest_framework import serializers, viewsets

from clinic.models import Appointment, AppointmentSlot, Doctor
from clinic.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from clinic.serializers import (
    AppointmentSerializer,
    AppointmentSlotSerializer,
    DoctorSerializer,
)


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


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        queryset = Appointment.objects.select_related(
            "patient",
            "slot",
            "slot__doctor",
        ).all()

        if not self.request.user.is_staff:
            queryset = queryset.filter(patient=self.request.user)

        status = self.request.query_params.get("status")
        doctor = self.request.query_params.get("doctor")
        date = self.request.query_params.get("date")
        slot = self.request.query_params.get("slot")

        if status:
            queryset = queryset.filter(status=status)

        if doctor:
            queryset = queryset.filter(slot__doctor_id=doctor)

        if date:
            queryset = queryset.filter(slot__date=date)

        if slot:
            queryset = queryset.filter(slot_id=slot)

        return queryset

    def perform_create(self, serializer):
        with transaction.atomic():
            slot = AppointmentSlot.objects.select_for_update().get(
                pk=serializer.validated_data["slot"].pk
            )

            if not slot.is_available or Appointment.objects.filter(
                slot=slot,
                status="booked",
            ).exists():
                raise serializers.ValidationError("This slot is already booked.")

            serializer.save(patient=self.request.user, slot=slot)
            slot.is_available = False
            slot.save(update_fields=["is_available"])

    def perform_update(self, serializer):
        appointment = serializer.instance
        old_status = appointment.status
        new_status = serializer.validated_data.get("status", old_status)

        with transaction.atomic():
            slot = AppointmentSlot.objects.select_for_update().get(
                pk=appointment.slot_id
            )

            if new_status == "booked" and old_status != "booked":
                has_active_booking = Appointment.objects.filter(
                    slot=slot,
                    status="booked",
                ).exclude(pk=appointment.pk).exists()

                if not slot.is_available or has_active_booking:
                    raise serializers.ValidationError("This slot is already booked.")

            appointment = serializer.save()

            if old_status == "booked" and appointment.status == "cancelled":
                has_active_booking = Appointment.objects.filter(
                    slot=slot,
                    status="booked",
                ).exclude(pk=appointment.pk).exists()

                if not has_active_booking:
                    slot.is_available = True
                    slot.save(update_fields=["is_available"])

            elif appointment.status == "booked":
                slot.is_available = False
                slot.save(update_fields=["is_available"])

    def perform_destroy(self, instance):
        slot = instance.slot
        was_booked = instance.status == "booked"

        instance.delete()

        if was_booked and not Appointment.objects.filter(
            slot=slot,
            status="booked",
        ).exists():
            slot.is_available = True
            slot.save(update_fields=["is_available"])
