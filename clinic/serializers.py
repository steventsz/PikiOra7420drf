from rest_framework import serializers

from clinic.models import Appointment, AppointmentSlot, Doctor


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


class AppointmentSerializer(serializers.ModelSerializer):
    patient_username = serializers.CharField(source="patient.username", read_only=True)
    doctor_name = serializers.CharField(source="slot.doctor.name", read_only=True)
    slot_date = serializers.DateField(source="slot.date", read_only=True)
    slot_time = serializers.CharField(source="slot.get_slot_index_display", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "patient_username",
            "slot",
            "doctor_name",
            "slot_date",
            "slot_time",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "patient",
            "patient_username",
            "doctor_name",
            "slot_date",
            "slot_time",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        #Check if the user is logged in
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("You must be logged in to book appointments.")
        #Existing appointments cannot change 'slot'
        if self.instance and "slot" in attrs and attrs["slot"] != self.instance.slot:
            raise serializers.ValidationError(
                "The slot for an existing appointment cannot be changed. "
                "Cancel this appointment and book another slot instead."
            )
        #Retrieve data from the front end and then the back end. Otherwise, it will update automatically.
        status = attrs.get("status", getattr(self.instance, "status", "booked"))
        slot = attrs.get("slot", getattr(self.instance, "slot", None))
        #New reservations must be 'booked'
        if not self.instance and status != "booked":
            raise serializers.ValidationError("New appointments must be created as booked.")
        #Check if the 'slot' is available for booking
        if status == "booked" and slot:
            active_appointments = Appointment.objects.filter(
                slot=slot,
                status="booked",
            )
            #Exclude yourself from the update
            if self.instance:
                active_appointments = active_appointments.exclude(pk=self.instance.pk)

            if active_appointments.exists():
                raise serializers.ValidationError("This slot is already booked.")
            #'current_booking' is used to prevent false positives
            current_booking = (
                self.instance
                and self.instance.slot_id == slot.id
                and self.instance.status == "booked"
            )
            #Check if the 'slot' is available
            if not current_booking and not slot.is_available:
                raise serializers.ValidationError("This slot is not available.")

        return attrs
