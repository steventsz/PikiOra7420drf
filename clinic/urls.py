from django.urls import path

from clinic.views import index

urlpatterns = [
    path("",index, name="index"),
]