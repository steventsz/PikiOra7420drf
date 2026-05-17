from django.urls import include, path
from rest_framework.routers import DefaultRouter

from clinic.views import LoginView, RegisterView, UserView
from clinic.viewsets import AppointmentSlotViewSet, AppointmentViewSet, DoctorViewSet

router = DefaultRouter()
router.register("doctors", DoctorViewSet, basename="doctor")
router.register("slots", AppointmentSlotViewSet, basename="slot")
router.register("appointments", AppointmentViewSet, basename="appointment")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/user/", UserView.as_view(), name="user"),
]
