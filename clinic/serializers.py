from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from clinic.models import Appointment, AppointmentSlot, Doctor


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "date_joined",
            "last_login",
        ]
        read_only_fields = [
            "id",
            "username",
            "date_joined",
            "last_login",
        ]


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

    def validate_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError("Slot date cannot be in the past.")

        return value

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
    patient = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
    )
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

        patient_was_provided = "patient" in attrs
        patient = attrs.get("patient")

        if self.instance:
            if (
                patient_was_provided
                and not request.user.is_staff
                and patient != self.instance.patient
            ):
                raise serializers.ValidationError(
                    "You cannot change the patient for this appointment."
                )
        else:
            if request.user.is_staff and not patient_was_provided:
                raise serializers.ValidationError(
                    "Staff users must choose a patient for the appointment."
                )

            if (
                patient_was_provided
                and not request.user.is_staff
                and patient != request.user
            ):
                raise serializers.ValidationError(
                    "You cannot create an appointment for another patient."
                )

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
            if not slot.doctor.is_active:
                raise serializers.ValidationError(
                    "Appointments cannot be booked with an inactive doctor."
                )

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
