from rest_framework import serializers

from clinic.models import AppointmentSlot, Doctor


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id',
                  'name',
                  'specialty',
                  'bio',
                  'email',
                  'phone',
                  'is_active',
                  'created_at',
                  'updated_at'
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AppointmentSlotSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)
    slot_time = serializers.CharField(source="get_slot_index_display", read_only=True)

    class Meta:
        model = AppointmentSlot
        fields = [
            "id",
            "doctor",
            "doctor_name",
            "date",
            "slot_index",
            "slot_time",
            "is_available",
            "created_at",
        ]
        read_only_fields = ["id", "doctor_name", "slot_time", "created_at"]

    def validate(self, attrs):
        doctor = attrs.get("doctor", getattr(self.instance, "doctor", None))
        date = attrs.get("date", getattr(self.instance, "date", None))
        slot_index = attrs.get("slot_index", getattr(self.instance, "slot_index", None))

        if doctor and date and slot_index:
            duplicate_slots = AppointmentSlot.objects.filter(
                doctor=doctor,
                date=date,
                slot_index=slot_index,
            )

            if self.instance:
                duplicate_slots = duplicate_slots.exclude(pk=self.instance.pk)
                #When checking for duplicates, do not include the record currently being updated.

            if duplicate_slots.exists():
                raise serializers.ValidationError(
                    "This doctor already has a slot at this date and time."
                )

        return attrs
