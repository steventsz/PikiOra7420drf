from django.urls import include, path
from rest_framework.routers import DefaultRouter

from clinic.views import LoginView, MeView, RegisterView
from clinic.viewsets import (
    AppointmentSlotViewSet,
    AppointmentViewSet,
    DoctorViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("doctors", DoctorViewSet, basename="doctor")
router.register("slots", AppointmentSlotViewSet, basename="slot")
router.register("appointments", AppointmentViewSet, basename="appointment")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
]
