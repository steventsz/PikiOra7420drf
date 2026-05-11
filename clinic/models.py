from django.contrib.auth.models import User
from django.db import models


class Doctor(models.Model):
    # Basic doctor information for display and booking.
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class AppointmentSlot(models.Model):
    # Each slot_index maps to one fixed 30-minute consultation period.
    SLOT_CHOICES = [
        (1, "09:00 - 09:30"),
        (2, "09:30 - 10:00"),
        (3, "10:00 - 10:30"),
        (4, "10:30 - 11:00"),
        (5, "11:00 - 11:30"),
        (6, "11:30 - 12:00"),
        (7, "13:00 - 13:30"),
        (8, "13:30 - 14:00"),
        (9, "14:00 - 14:30"),
        (10, "14:30 - 15:00"),
        (11, "15:00 - 15:30"),
        (12, "15:30 - 16:00"),
    ]

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="slots",
    )
    date = models.DateField()
    slot_index = models.PositiveSmallIntegerField(choices=SLOT_CHOICES)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "slot_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "date", "slot_index"],
                name="clinic_unique_doctor_date_slot",
            ),
        ]

    def __str__(self):
        return f"{self.doctor.name} - {self.date} - {self.get_slot_index_display()}"


class Appointment(models.Model):
    # A patient books one generated slot on a given date.
    STATUS_CHOICES = [
        ("booked", "Booked"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    slot = models.ForeignKey(
        AppointmentSlot,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="booked",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["patient", "status"])]

    def __str__(self):
        return f"{self.patient.username} - {self.slot}"
