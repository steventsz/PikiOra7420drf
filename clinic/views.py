from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from clinic.models import Doctor
from clinic.serializers import DoctorSerializer


# Create your views here.
def index(request):
    # doctors = Doctor.objects.all()
    # data = {
    #     'doctors': list(doctors.values())
    # }
    doctors = DoctorSerializer(Doctor.objects.all(), many=True).data
    return JsonResponse(doctors, safe=False)

@api_view(['GET'])
def doctors_detail(request):
    doctors = Doctor.objects.all()
    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def doctors_create(request):
    serializer = DoctorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['PUT'])
def doctors_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    serializer = DoctorSerializer(doctor)
    if serializer.update(doctor, request.data):
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
def doctors_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    doctor.delete()
    return Response(status=204)
