from rest_framework import serializers

from clinic.models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'name', 'specialty', 'bio', 'email', 'phone', 'is_active', 'created_at', 'updated_at']