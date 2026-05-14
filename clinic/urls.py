from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from clinic.viewsets import AppointmentSlotViewSet, DoctorViewSet

router = DefaultRouter()
router.register("doctors", DoctorViewSet, basename="doctor")
router.register("slots", AppointmentSlotViewSet, basename="slot")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/login/", obtain_auth_token, name="auth-login"),
]
