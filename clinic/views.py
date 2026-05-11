from django.http import JsonResponse

from clinic.models import Doctor


# Create your views here.
def index(request):
    doctors = Doctor.objects.all()
    data = {
        'doctors': list(doctors.values())
    }
    return JsonResponse(data)

